# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import random
import string
from datetime import date

import factory
from factory import declarations


def current_year():
    return date.today().year


def formatted_date(month, day, year=None):
    """
    Returns date formatted in MM/DD/YYYY format.  If year isn't passed in, it
    will default to the current year.
    """
    return date(year or current_year(), month, day).strftime('%m/%d/%Y')


def random_chars(n=4, chars=None):
    if chars is None:
        chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(n))


class UniqueIdAttribute(declarations.BaseDeclaration):
    """
    Returns a random 32-character string.

    Use for disambiguation with ID-like fields to avoid the ODS API duplicate
    detection facility (wherein if you create a resource identical in business
    logic to an existing resource, the existing resource will be returned
    instead of creating a new one.)
    """
    num_chars = 32

    def __init__(self, num_chars=None, **kwargs):
        self.num_chars = num_chars or self.num_chars
        super(UniqueIdAttribute, self).__init__(**kwargs)

    def evaluate(self, instance, step, extra):
        return random_chars(self.num_chars, string.ascii_lowercase + string.digits)


class UniquePrimaryKeyAttribute(declarations.BaseDeclaration):
    """
    Returns a positive integer less than SQL Server's maxint.

    Use for primary key fields to prevent clashes and deduplication logic (see
    docstring for `UniqueIdAttribute` above.)
    """
    MAXINT = 2147483647

    def evaluate(self, instance, step, extra):
        return random.randint(0, self.MAXINT)


class RandomDateAttribute(declarations.BaseDeclaration):
    """
    Returns a random date between 1/1/1901 and 12/12/max_year.  Ignores days
    of the month past the 28th.
    """
    max_year = 9999

    def __init__(self, max_year=None, **kwargs):
        self.max_year = max_year or self.max_year
        super(RandomDateAttribute, self).__init__(**kwargs)

    def evaluate(self, instance, step, extra):
        return formatted_date(
            random.randint(1, 12),
            random.randint(1, 28),
            random.randint(1901, self.max_year)
        )


class RandomSuffixAttribute(factory.LazyAttribute):
    """
    Subclasses `factory.LazyAttribute` to append a random string of characters.

    This can be used for disambiguation between string-based business keys (see
    docstring for `UniqueIdAttribute` above.)
    """
    def __init__(self, func, *args, **kwargs):
        if isinstance(func, basestring):
            unformatted_string = str(func)
            func = lambda o: unformatted_string
        self._suffix_length = kwargs.pop('suffix_length', 4)
        super(RandomSuffixAttribute, self).__init__(func, *args, **kwargs)

    def evaluate(self, instance, step, extra):
        result = super(RandomSuffixAttribute, self).evaluate(instance, step, extra)
        return '{} {}'.format(result, self._suffix(self._suffix_length))

    @staticmethod
    def _suffix(length=4):
        return random_chars(length)
