# ------------------------------------------------------------------------------
# copyright.py - Script to check for correctly formatted copyright notices
#
# August 2022, Gurkiran Singh
#
# Copyright (c) 2022
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

from datetime import date

import argparse
import os
import re
import sys

import cmn

LINE_LENGTH = 80


class _CopyrightCheckReturnCodes(cmn.ReturnCodes):
    SUCCESS = 0
    CHANGES_REQUIRED = 1


def _generate_expected(file_path):
    """
    Generator tha outputs each line of a correctly formatted copyright notice.

    :param file_path:
        Path to the file to generate an copyright notice for.

    :yield:
        Regex for a copyright notice, output line-by-line.
    """
    file_name = file_path.split("/")[-1]
    exp = [
        "# -----------------------------------------------------------------------------",
        f"# {file_name} - [^.*]",
        "#",
        "# (January|February|March|April|May|June|July|August|September|October|November|December)"
        r" 20[0-9]{2}, [A-Za-z -]",
        "#",
        rf"# Copyright \(c\) (20[0-9]{{2}} - ){{0,1}}{date.today().year}",
        "# All rights reserved.",
        "# -----------------------------------------------------------------------------",
    ]

    for line in exp:
        yield line


def _run_check(_):
    """
    Runs copyright checks on input parameters.

    :param args:
        Namespace object with args to run check on.
    """
    include_files = cmn.get_all_code_files()

    failed = {}
    for file in include_files:
        print(include_files, file)
        if os.stat(file).st_size == 0:
            continue
        with open(file, "r") as f_read:
            for exp_line in _generate_expected(file):
                line = f_read.readline().strip("\n")
                if not re.match(exp_line, line):
                    failed[file] = line
                    break

    if failed:  # pylint: disable=no-else-return
        print(
            "Copyright notice checks failed! "
            "The following files need to be fixed:"
        )
        for file, line in failed.items():
            print(f"   - {file}: {line}")
        return _CopyrightCheckReturnCodes.CHANGES_REQUIRED
    else:
        print(
            "Copyright notice checks succeeded! "
            "However, a manual confirmation is always recommended."
        )
        return _CopyrightCheckReturnCodes.SUCCESS


def main():
    """Main function for copyright checker CLI. Parses and handles CLI input."""
    parser = argparse.ArgumentParser(
        description="Check if all files have correctly formatted copyright checks. "
        "Optionally add/modify the notice on any files that fail the check."
    )

    args = parser.parse_args()

    sys.exit(_run_check(args))


if __name__ == "__main__":
    main()
