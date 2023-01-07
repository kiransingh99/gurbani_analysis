# ------------------------------------------------------------------------------
# _cmn.py - Common file for Gurbani Analysis CLI
#
# October 2022, Gurkiran Singh
#
# Copyright (c) 2022
# All rights reserved.
# ------------------------------------------------------------------------------

"""Common objects Gurbani Analysis CLI."""

from __future__ import annotations

__all__ = [
    "Error",
    "RC",
    "Verbosity",
]

from typing import Optional

import enum


class Error(Exception):
    """
    Base error class for all errors in the Gurbani Analysis CLI.
    """

    def __init__(self, msg: str, suggested_steps: Optional[list[str]] = None):
        self.msg = msg
        self.suggested_steps = suggested_steps

    def __str__(self) -> str:
        output = "\nError: "
        output += self.msg + "\n"
        if self.suggested_steps:
            output += " Suggested steps:\n"
            for step in self.suggested_steps:
                output += f"  - {step}\n"

        return output


class NotImplementedException(Error):
    def __init__(self, traceback: str):
        msg = "This code path was not implemented.\n" + traceback
        suggested_steps = [
            "Contact the developers and explain the steps to recreate this error."
        ]
        super().__init__(msg, suggested_steps)


class RC(enum.Enum):
    """
    Return codes that can be output from this script.
    """

    SUCCESS = "00"

    # Misc errors
    UNHANDLED_ERROR = "10"

    # Development errors
    NOT_IMPLEMENTED = "90"

    def is_ok(self) -> bool:
        """
        Determines if error shows that an error has occurred.

        :return:
            True if error code does not signify an error, False otherwise.
        """
        return self in [self.SUCCESS]


class UnhandledExceptionError(Error):
    def __init__(self, msg: str = None):
        msg = "The following exception was not handled:\n" + msg
        super().__init__(msg)


class Verbosity(enum.Enum):
    """
    Verbosity of output from CLI.
    """

    SUPPRESSED = 0
    STANDARD = 1
    VERBOSE = 2
    VERY_VERBOSE = 3

    def is_suppressed(self) -> bool:
        """
        Check if verbosity is suppressed.

        :return:
            True if verbosity is suppressed. False otherwise.
        """
        return self in [Verbosity.SUPPRESSED]

    def is_very_verbose(self) -> bool:
        """
        Check if verbosity is very verbose.

        :return:
            True if verbosity is very verbose. False otherwise.
        """
        return self in [Verbosity.VERY_VERBOSE]

    def is_verbose(self) -> bool:
        """
        Check if verbosity is either verbose or very verbose.

        :return:
            True if verbosity is verbose or very verbose. False otherwise.
        """
        return self in [Verbosity.VERBOSE, Verbosity.VERY_VERBOSE]
