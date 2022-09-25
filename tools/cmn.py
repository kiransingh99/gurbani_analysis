# ------------------------------------------------------------------------------
# cmn.py - Common tools file
#
# September 2022, Gurkiran Singh
#
# Copyright (c) 2022
# All rights reserved.
# ------------------------------------------------------------------------------

"""Common objects for all tools scripts."""

__all__ = [
    "ReturnCodes",
    "get_all_code_files",
    "get_python_files",
    "handle_cli_error",
]

import enum
import re
import subprocess
import sys


class ReturnCodes(enum.IntEnum):
    """Subclass for all return code enums."""

    @classmethod
    def get_error_codes(cls):
        """Returns a list of all the known error code values."""
        return [error.value for error in cls]


def get_all_code_files(untracked_files=False, root_dir="."):
    """
    Produces a set of source code files in the given directory.

    :param untracked_files:
        If True, files not tracked by git will be included in the search.
        Eefaults to False.

    :param root_dir:
        All files must be a subdirectory of this one. Relative to root of ws.

    :return:
        A set of files filtered with the given settings.
    """

    exclude_patterns = {
        ".github/*",
        "artifacts/*",
        "README.md",
        ".pylintrc",
    }

    try:
        tracked_files_output = subprocess.run(
            "git ls-files", capture_output=True, check=True
        )
    except Exception as exc:
        print(exc)
    else:
        unfiltered = set(tracked_files_output.stdout.decode("utf-8").split("\n"))

        if untracked_files:
            untracked_files_output = subprocess.run(
                "git ls-files --others", capture_output=True, check=True
            )
            unfiltered.update(
                set(untracked_files_output.stdout.decode("utf-8").split("\n"))
            )

        unfiltered.discard("")

        if root_dir == ".":
            filtered = set(unfiltered)
        else:
            filtered = set()
            for file in unfiltered:
                if file.startswith(root_dir):
                    filtered.add(file)

        unfiltered = filtered
        filtered = set()
        for file in unfiltered:
            exclude = False
            for pattern in exclude_patterns:
                if re.match(pattern, file):
                    exclude = True
                    break
            if not exclude:
                filtered.add(file)

        return filtered


def get_python_files(untracked_files=False, root_dir="."):
    """
    Produces a set of python files in the given directory.

    :param untracked_files:
        If True, files not tracked by git will be included in the search.
        Eefaults to False.

    :param root_dir:
        All files must be a subdirectory of this one. Relative to root of ws.

    :return:
        A set of python files filtered with the given settings.
    """
    unfiltered = get_all_code_files(untracked_files, root_dir)

    filtered = set()
    for file in unfiltered:
        if file.endswith(".py"):
            filtered.add(file)

    return filtered


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
        The original exception, which will get reraised.

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
