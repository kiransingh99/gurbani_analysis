# ------------------------------------------------------------------------------
# _cmn.py - Common file for Gurbani Analysis CLI
#
# October 2022, Gurkiran Singh
#
# Copyright (c) 2022
# All rights reserved.
# ------------------------------------------------------------------------------

"""Common objects Gurbani Analysis CLI."""

__all__ = [
    "Error",
    "RC",
    "Verbosity",
    "datetime_to_str",
    "str_to_datetime",
]

from datetime import datetime

import enum


class Error(Exception):
    """
    Base error class for all errors in the Gurbani Analysis CLI.
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


class RC(enum.Enum):
    """
    Return codes that can be output from this script.
    """

    SUCCESS = "000"

    # Misc errors
    #

    def is_ok(self):
        """
        Determines if error shows that an error has occurred.

        :return:
            True if error code does not signify an error, False otherwise.
        """
        return self in [self.SUCCESS]


class Verbosity(enum.Enum):
    """
    Verbosity of output from CLI.
    """

    SUPPRESSED = 0
    STANDARD = 1
    VERBOSE = 2
    VERY_VERBOSE = 3

    def is_suppressed(self):
        """
        Check if verbosity is suppressed.

        :return:
            True if verbosity is suppressed. False otherwise.
        """
        return self in [Verbosity.SUPPRESSED]

    def is_very_verbose(self):
        """
        Check if verbosity is very verbose.

        :return:
            True if verbosity is very verbose. False otherwise.
        """
        return self in [Verbosity.VERY_VERBOSE]

    def is_verbose(self):
        """
        Check if verbosity is either verbose or very verbose.

        :return:
            True if verbosity is verbose or very verbose. False otherwise.
        """
        return self in [Verbosity.VERBOSE, Verbosity.VERY_VERBOSE]


def datetime_to_str(date, date_format):
    """
    Converts a datetime object into a string of the given format.

    :param date:
        `datetime` object to be converted.

    :param date_format:
        Format of output date.

    :return:
        String representation of the given date.
    """
    return datetime.strftime(date, date_format)


def str_to_datetime(date, date_format):
    """
    Converts a date string of the given format, to a `datetime` object.

    :param date:
        Date to be converted.

    :param date_format:
        Format of given date.

    :return:
        `datetime` object representing the given date.
    """
    return datetime.strptime(date, date_format)
