# ------------------------------------------------------------------------------
# cmn.py - Common tools file
#
# September 2022, Gurkiran Singh
#
# Copyright (c) 2022
# All rights reserved.
# ------------------------------------------------------------------------------

"""Common objects for all tools scripts."""

import enum
import sys


class ReturnCodes(enum.IntEnum):
    """Subclass for all return code enums."""

    @classmethod
    def get_error_codes(cls):
        """Returns a list of all the known error code values."""
        return [error.value for error in cls]


def handle_cli_error(known_return_codes, return_code, cmd, exc=None):
    """
    Handles the exception raised due to a failure occurring when running a CLI.
    If there's an unknown error code, an error message is printed to
    log this. The script then exits with the same return code as received from
    the CLI.

    :param known_return_codes:
        Enum containing all known error codes.

    :param return_code:
        Return code of the failed CLI.

    :param cmd:
        The command ran, as a list of each argument of the command.

    :param exc:
        The original exception raised, which will get reraised.

    :raises Exception:
        If `exc` was provided, it gets raised again.
    """

    if return_code not in known_return_codes.get_error_codes():
        print(
            "\nAn unexpected error occurred when running the command:"
            + {" ".join(cmd)}
        )
        if exc:
            raise exc

    sys.exit(return_code)
