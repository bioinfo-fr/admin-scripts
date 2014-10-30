# -*- coding: utf-8 -*-
# Manage users
# Bioinfo-fr planning

import csv
import os
import datetime
import random
from collections import deque

# the file referencing the user
users_file = '%s.csv' % os.path.splitext(__file__)[0]

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
    >>>     print get(users, 'status', '-')
    >>>     print get(users, 'role', ['admin', 'auteur'])
    """
    if isinstance(values, str):
        values = [values]
    values = [v.lower() for v in values]
    return [u for u in users for v in values if v in u[key.upper()].lower().split('|')]


def calendar(start=(2013, 10, 1), end=(2013, 12, 21)):
    """
    Start the next monday.
    """
    start = datetime.date(*start) + datetime.timedelta(7 - datetime.date(*start).weekday())
    end = datetime.date(*end) + datetime.timedelta(7 - datetime.date(*end).weekday())

    def _next(start, end):
        """
        Generate tthe days
        """
        while start < end:
            start += datetime.timedelta(days=7)
            yield start
        raise StopIteration

    for day in _next(start, end):
        yield display_date(day)


def _pick_authors(authors):
    store = list(authors)
    while True:
        try:
            yield store.pop()
        except IndexError:
            store = list(authors)
            yield store.pop()


def _make_reviewer_list(admins, authors, reviewers_only):
    l = admins + authors * 2 + reviewers_only * 5
    random.shuffle(l)
    return l


def _pick_reviewer(reviewers):
    while True:
        yield random.sample(reviewers, 1)[0]


def main(start=(2013, 04, 25), end=(2013, 11, 01)):
    users = load(users_file)

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
    for d, a, r in main():
        print '%s :: %s :: %s' % (d, a, ' - '.join((x for x in r)))
