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
    def error_codes(cls):
        """Returns a list of all the known error code values."""
        return [error.value for error in cls]


def handle_cli_error(KnownReturnCodes, return_code, cmd, exc=None):
    """
    Handles the exception raised due to a failure occurring when running a CLI.
    If there's an unknown error code, an error message is printed to
    log this. The script then exits with the same return code as received from
    the CLI.

    :param KnownReturnCodes:
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

    try:
        breakpoint()
        # Check if return code is known.
        return_code in KnownReturnCodes.error_codes
    except ValueError:
        print(
            "\nAn unexpected error occurred when running the command:"
            + {" ".join(cmd)}
        )
        if exc:
            raise exc
    finally:
        sys.exit(return_code)
