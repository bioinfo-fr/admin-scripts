# -*- coding: utf-8 -*-
"""Bioinfo-fr Planning.

Usage:
  user.py <start> <end> [--path=<path>]
  user.py (-h | --help)
  user.py --version

Options:
  --path=<path>    Path of the user file [default: users.csv].
  -h --help        Show this screen.
  --version        Show version.

Description:
    <start>        The start date (yyyy,mm,dd)
    <end>          The end date (yyyy,mm,dd)
"""
from docopt import docopt
import csv
import os
import datetime
import random
from collections import deque


display_date = lambda x: datetime.datetime.strftime(x, '%A %d %B %Y')


def load(path):
    """
    Load users from csv file.
    """
    users = []
    with open(path, 'rb') as infile:
        reader = csv.DictReader(infile, delimiter=',', quoting=csv.QUOTE_NONE)
        users = [r for r in reader]
    return users


def get(users, key, values):
    """
    Get from an users list the key. Filter by value.
    e.g:
    >>>     users = load(users_file)
    >>>     print get(users, 'firstname', 'yohan')
    >>>     print get(users, 'role', ['admin', 'auteur'])
    """
    if isinstance(values, str):
        values = [values]
    values = [v.lower() for v in values]
    return [u for u in users for v in values if v in u[key.upper()].lower().split('|')]


def calendar(start, end):
    """
    Start the next monday.
    """
    start += datetime.timedelta(7 - start.weekday())
    end += datetime.timedelta(7 - end.weekday())

    def _next(start, end):
        """
        Generate the days
        """
        while start < end:
            start += datetime.timedelta(days=7)
            yield start
        raise StopIteration

    for day in _next(start, end):
        yield display_date(day)


def _pick_authors(authors):
    shuffled_authors = list(authors)
    random.shuffle(shuffled_authors)
    store = list(shuffled_authors)
    while True:
        try:
            yield store.pop()
        except IndexError:
            store = list(shuffled_authors)
            yield store.pop()


def _make_reviewer_list(admins, authors, reviewers_only):
    l = admins + authors * 2 + reviewers_only * 5
    random.shuffle(l)
    return l


def _pick_reviewer(reviewers):
    while True:
        yield random.sample(reviewers, 1)[0]


def main(path, start, end):
    users = load(path)

    admins = get(users, 'role', 'admin')
    authors = get(users, 'role', 'auteur')
    reviewers_only = [i for i in get(users, 'role', 'relecteur') if i not in authors]

    author_picker = _pick_authors(authors)
    reviewers_picker = _pick_reviewer(_make_reviewer_list(admins, authors, reviewers_only))

    current_authors = deque([], 6)
    current_reviewer = deque([], 3 * 3)

    for day in calendar(start, end):
        auth = author_picker.next()['PSEUDO']
        current_authors.append(auth)

        revs = []
        for i in xrange(3):
            rev = reviewers_picker.next()['PSEUDO']
            while rev in current_authors or rev in current_reviewer or rev in revs:
                rev = reviewers_picker.next()['PSEUDO']
            revs.append(rev)
            current_reviewer.append(rev)

        yield day, auth, revs

if __name__ == '__main__':
    args = docopt(__doc__, version='Planning 2.0')
    start = datetime.datetime.strptime(args['<start>'], "%Y,%m,%d")
    end = datetime.datetime.strptime(args['<end>'], "%Y,%m,%d")
    path = args['--path']
    for day, author, reviewers in main(path, start, end):
        print '%s :: %s :: %s' % (day, author, ' - '.join((x for x in reviewers)))
