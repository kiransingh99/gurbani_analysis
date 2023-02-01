# ------------------------------------------------------------------------------
# cmn.py - Common tools file
#
# September 2022, Gurkiran Singh
#
# Copyright (c) 2022 - 2023
# All rights reserved.
# ------------------------------------------------------------------------------

"""Common objects for all tools scripts."""

from __future__ import annotations

__all__ = [
    "ReturnCodes",
    "get_all_code_files",
    "get_python_files",
    "handle_cli_error",
    "month_name_from_num",
    "which_python",
]

from collections.abc import Iterable
from typing import Optional

import enum
import re
import subprocess
import sys


class ReturnCodes(enum.IntEnum):
    """Subclass for all return code enums."""

    @classmethod
    def get_error_codes(cls) -> list[int]:
        """Returns a list of all the known error code values.

        :return: a list of all the error code values.
        """
        return [error.value for error in cls]

    @classmethod
    def is_ok(cls, value: int) -> bool:
        """A return code is okay if it is 0.

        :return: True if the return code does not imply any issues. False
            otherwise.
        """
        return value == 0


class WinErrorCodes(ReturnCodes):
    """WINError codes."""

    OK = 0
    FILE_NOT_FOUND = 2


def get_all_code_files(
    untracked_files: bool = False, root_dir: str = "."
) -> set[str]:
    """Produces a set of source code files tracked by git, in the given
    directory.

    :param untracked_files: if True, files not tracked by git will be included
        in the search. Defaults to False.
    :param root_dir: all files must be a subdirectory of this one. Relative to
        root of ws.
    :return: a set of files filtered with the given settings.
    """

    exclude_patterns = {
        ".github/*",
        "artifacts/*",
        ".gitignore",
        ".pylintrc",
        "README.md",
    }

    tracked_files_output = subprocess.run(
        ["git", "ls-files"], capture_output=True, check=True
    )

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


def get_python_files(
    untracked_files: bool = False, root_dir: str = "."
) -> set[str]:
    """Produces a set of python files in the given directory.

    :param untracked_files: if True, files not tracked by git will be included
        in the search. Defaults to False.
    :param root_dir: all files must be a subdirectory of this one. Relative to
        root of ws.
    :return: a set of python files filtered with the given settings.
    """
    unfiltered = get_all_code_files(untracked_files, root_dir)

    filtered = set()
    for file in unfiltered:
        if file.endswith(".py"):
            filtered.add(file)

    return filtered


def handle_cli_error(
    known_return_codes: ReturnCodes,
    return_code: int,
    cmd: Iterable[str],
    exc: Optional[Exception] = None,
) -> None:
    """Handles the exception raised due to a failure occurring when running a
    CLI. If there's an unknown error code, an error message is printed to log
    this. The script then exits with the same return code as received from the
    CLI.

    :param known_return_codes: enum containing all known error codes.
    :param return_code: return code of the failed CLI.
    :param cmd: the command ran, as a list of each argument of the command.
    :param exc: the original exception, which will get reraised.
    :raises Exception: if `exc` was provided, it gets raised again.
    """
    if return_code not in known_return_codes.get_error_codes():
        print(
            "\nAn unexpected error occurred when running the command:"
            + " ".join(cmd)
        )
        if exc:
            raise exc

    sys.exit(return_code)


def handle_missing_package_error(package: str) -> None:
    """Handler for when a package is missing.

    :param package: name of missing package.
    """
    print(f"Failed running command. Check `{package}` is installed.")


def month_name_from_num(index: int) -> str:
    """Converts a number into the corresponding month.

    :param index: number between 1 and 12.
    :return: month name corresponding to input.
    """
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    return months[index - 1]


def which_python() -> str:
    """Determine how to invoke python 3.

    :return: correct invocation of python on the running computer.
    """
    options = ["python3", "python"]

    for option in options:
        try:
            subprocess.run(["which", option], capture_output=True, check=True)
        except subprocess.CalledProcessError:
            pass
        else:
            return option

    raise FileNotFoundError  # can't find python on this system
