# ------------------------------------------------------------------------------
# main.py - Common file for Gurbani Analysis CLI
#
# October 2022, Gurkiran Singh
#
# Copyright (c) 2022
# All rights reserved.
# ------------------------------------------------------------------------------

"""Common objects Gurbani Analysis CLI."""

__all__ = []

from dataclasses import dataclass
from datetime import datetime

import enum


class Verbosity(enum.Enum):
    """
    FAIL_COMMIT TODO
    """

    STANDARD = 0
    VERBOSE = 1
    VERY_VERBOSE = 2
    SUPPRESSED = 3

    def is_verbose(self):
        """
        FAIL_COMMIT TODO

        :return: _description_
        """
        return self in [Verbosity.VERBOSE, Verbosity.VERY_VERBOSE]

    def is_very_verbose(self):
        """
        FAIL_COMMIT TODO

        :return: _description_
        """
        return self in [Verbosity.VERY_VERBOSE]

    def is_suppressed(self):
        """
        FAIL_COMMIT TODO

        :return: _description_
        """
        return self in [Verbosity.SUPPRESSED]


class RC(enum.Enum):
    """
    FAIL_COMMIT TODO
    """

    SUCCESS = "000"

    # Misc errors
    CLI_BACKEND_ERROR = "101"

    # FAIL_COMMIT

    def is_ok(self):
        """
        Determines if error shows that an error has occurred.

        :return:
            True if error code does not signify an error, False otherwise.
        """
        return self in [self.SUCCESS]


class Error(Exception):
    """
    FAIL_COMMIT TODO
    """

    def __init__(self, msg, suggested_steps=None):
        self.msg = msg
        self.suggested_steps = suggested_steps

    def __str__(self):
        output = "\nError: "
        output += self.msg + "\n"
        if self.suggested_steps:
            output += " Suggested steps:\n"
            for step in self.suggested_steps:
                output += f"  - {step}\n"

        return output


def datetime_to_str(date, format):
    """
    Converts a datetime object into a string of the given format.

    :param date:
        `datetime` object to be converted.

    :param format:
        Format of output date.

    :return:
        String representation of the given date.
    """
    return datetime.strftime(date, format)


def str_to_datetime(date, format):
    """
    Converts a date string of the given format, to a `datetime` object.

    :param date:
        Date to be converted.

    :param format:
        Format of given date.

    :return:
        `datetime` object representing the given date.
    """
    return datetime.strptime(date, format)