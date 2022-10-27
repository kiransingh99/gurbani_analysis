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

from black import out


class RC(enum.Enum):
    """
    FAIL_COMMIT TODO
    """

    SUCCESS = "000"

    # Misc errors
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
