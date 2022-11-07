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

import enum
from typing import Optional


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


@dataclass(frozen=True)
class Error(Exception):
    """
    FAIL_COMMIT TODO
    """

    msg: str
    suggested_steps: Optional[list] = None

    def __str__(self):
        output = "\nError: "
        output += self.msg + "\n"
        if self.suggested_steps:
            output += " Suggested steps:\n"
            for step in self.suggested_steps:
                output += f"  - {step}\n"

        return output
