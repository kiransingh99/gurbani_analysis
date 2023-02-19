# ------------------------------------------------------------------------------
# _cmn.py - Common file for Gurbani Analysis CLI
#
# November 2022, Gurkiran Singh
#
# Copyright (c) 2022 - 2023
# All rights reserved.
# ------------------------------------------------------------------------------

"""Common objects for the Gurbani Analysis CLI."""

from __future__ import annotations

__all__ = [
    "Error",
    "Logger",
    "NotImplementedException",
    "RC",
    "UnhandledExceptionError",
    "Verbosity",
]

from typing import Any, Optional

import enum
import logging


class Error(Exception):
    """Base error class for all errors in the Gurbani Analysis CLI."""

    def __init__(
        self,
        msg: str,
        *,
        rc: Optional[RC] = None,
        suggested_steps: Optional[list[str]] = None,
    ):
        self.rc = rc
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


class Logger:
    """Handles logging for the CLI."""

    def __init__(self, name: str):
        self.logger = logging.Logger(name)
        self.handler = logging.StreamHandler()
        self.logger.addHandler(self.handler)

    def _log(self, level: Verbosity, *msg: Any) -> None:
        """Logging function.

        :param level: level at which to log the message.
        :param *msg: message to log.
        """
        self.logger.log(level.value, "".join(str(item) for item in msg))

    def set_level(self, level: Verbosity) -> None:
        """Set the level of the logger.

        :param level: verbosity of logging output.
        """
        self.handler.setLevel(level.value)

    def suppressed(self, *msg: Any) -> None:
        """Suppressed level logging.

        :param *msg: message to log.
        """
        self._log(Verbosity.SUPPRESSED, *msg)

    def standard(self, *msg: str) -> None:
        """Standard level logging.

        :param msg: message to log.
        """
        self._log(Verbosity.STANDARD, *msg)

    def verbose(self, *msg: str) -> None:
        """Verbose level logging.

        :param msg: message to log.
        """
        self._log(Verbosity.VERBOSE, *msg)

    def very_verbose(self, *msg: str) -> None:
        """Very verbose level logging.

        :param msg: message to log.
        """
        self._log(Verbosity.VERY_VERBOSE, *msg)


class NotImplementedException(Error):
    """Custom error type for unimplemented code."""

    def __init__(self, traceback: str):
        msg = "This code path was not implemented.\n" + traceback
        suggested_steps = [
            "Contact the developers and explain the steps to recreate this error."
        ]
        super().__init__(msg, suggested_steps=suggested_steps)


class RC(enum.Enum):
    """Return codes that can be output from this script."""

    # Misc
    SUCCESS = "00"
    UNHANDLED_ERROR = "10"

    # Parser errors
    LOAD_WEBPAGE_ERROR = "20"
    SCRAPE_HTML_ERROR = "21"

    # Development errors
    NOT_IMPLEMENTED = "90"

    def is_ok(self) -> bool:
        """Determines if error shows that an error has occurred.

        :return: True if error code does not signify an error, False otherwise.
        """
        return self in [self.SUCCESS]


class UnhandledExceptionError(Error):
    """Custom error type to reraise when there's an unhandled exception raised
    by an imported library.
    """

    def __init__(self, msg: str):
        msg = "The following exception was not handled:\n" + msg
        super().__init__(msg)


class Verbosity(enum.Enum):
    """Verbosity of output from CLI."""

    SUPPRESSED = 25
    STANDARD = 20
    VERBOSE = 15
    VERY_VERBOSE = 10
