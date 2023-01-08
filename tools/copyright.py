# ------------------------------------------------------------------------------
# copyright.py - Script to check for correctly formatted copyright notices
#
# September 2022, Gurkiran Singh
#
# Copyright (c) 2022 - 2023
# All rights reserved.
# ------------------------------------------------------------------------------

"""Checks that a correctly formatted copyright notice is at the top of every
file in the repo. It should be formatted as follows:"""
# ------------------------------------------------------------------------------
# <file_name.py> - <Short description of file>
#
# <Month and year file was created>, <File creator>
#
# Copyright (c) <year file was created> - <current year>
# All rights reserved.
# ------------------------------------------------------------------------------

from __future__ import annotations

__all__: list[str] = []

from collections.abc import Generator
from dataclasses import dataclass
from datetime import date

import argparse
import os
import re
import subprocess
import sys

import cmn

LINE_LENGTH = 80


class _CopyrightCheckReturnCodes(cmn.ReturnCodes):
    """Possible exit codes from this copyright notice checker."""

    SUCCESS = 0
    CHANGES_REQUIRED = 1


@dataclass(frozen=True)
class _LineMatchInfo:
    """
    Structure to hold data about a given line of a copyright notice.

    Tracks the line number of the notice, the actual line read in from the file
    being tested, and the expected regex rule for the line.
    """

    line_number: int
    act_line: str
    exp_line: str


def _generate_expected(file_path: str) -> Generator[str, None, None]:
    """
    Generator that outputs each line of a correctly formatted copyright notice.

    :param file_path:
        Path to the file to generate an copyright notice for.

    :yield:
        Regex for a copyright notice, output line-by-line.
    """
    file_name = file_path.split("/")[-1]
    notice_start_end = r"^# [-]{78}$"
    blank_line = r"^#$"

    edit_dates = (
        subprocess.run(
            ["git", "log", "--format=%ci", "./" + file_path],
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .strip()
        .split("\n")
    )
    created_month = cmn.month_name_from_num(int(edit_dates[-1][5:7]))
    created_year = edit_dates[-1][:4]
    last_edited_year = edit_dates[0][:4]
    if created_year == last_edited_year:
        date_range = created_year
    else:
        date_range = created_year + " - " + last_edited_year

    exp = [
        notice_start_end,
        rf"^# {file_name} - .+$",
        blank_line,
        rf"^# {created_month} {created_year}, [A-Za-z -]+$",
        blank_line,
        rf"^# Copyright \(c\) {date_range}$",
        r"^# All rights reserved.$",
        notice_start_end,
    ]

    for line in exp:
        yield line


def _run_check(args: argparse.Namespace) -> int:
    """
    Runs copyright checks on input parameters.

    :param args:
        Namespace object with args to run check on.
    """
    failed = {}
    line_number = 0

    def read_line() -> str:
        nonlocal line_number
        line_number += 1
        return f_read.readline().strip("\n")

    include_files = cmn.get_all_code_files()

    for file in include_files:
        line_number = 0
        try:
            if os.stat(file).st_size == 0:  # empty file
                continue
        except FileNotFoundError:
            # If file has been deleted but git doesn't know yet
            continue
        with open(file, encoding="utf-8") as f_read:
            for exp_line in _generate_expected(file):
                line = read_line()
                if line.startswith("#!"):
                    line = read_line()
                if not re.match(exp_line, line):
                    failed[file] = _LineMatchInfo(
                        line_number,
                        act_line=line,
                        exp_line=exp_line,
                    )
                    break

    if failed:  # pylint: disable=no-else-return
        print(
            "Copyright notice checks failed! "
            "The following files need to be fixed:"
        )

        for file, line_info in failed.items():
            if args.show_regex:
                print(f"   - {file}:{line_info.line_number}:")
                print(f"        `{line_info.act_line}` does not match")
                print(f"        `{line_info.exp_line}`")
            else:
                print(
                    f"   - {file}:{line_info.line_number}:    `{line_info.act_line}`"
                )

        return _CopyrightCheckReturnCodes.CHANGES_REQUIRED
    else:
        print(
            "Copyright notice checks succeeded! "
            "However, a manual confirmation is always recommended."
        )
        return _CopyrightCheckReturnCodes.SUCCESS


def main() -> None:
    """Main function for copyright checker CLI. Parses and handles CLI input."""
    parser = argparse.ArgumentParser(
        description="Check if all files have correctly formatted copyright checks. "
        "Optionally add/modify the notice on any files that fail the check."
    )

    parser.add_argument(
        "-r",
        "--show-regex",
        action="store_true",
        help="If the check fails on a given file, provide the regex rule that "
        "the malformed line should match.",
    )

    args = parser.parse_args()

    sys.exit(_run_check(args))


if __name__ == "__main__":
    main()
