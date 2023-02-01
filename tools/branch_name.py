#!/usr/bin/python3
# ------------------------------------------------------------------------------
# branch_name.py - Check that the branch name is valid.
#
# October 2022, Gurkiran Singh
#
# Copyright (c) 2022 - 2023
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Checks if the current branch has an appropriate name before merging into main.
"""

from __future__ import annotations

__all__: list[str] = []


import re
import subprocess
import sys

import cmn


class _BranchNameReturnCodes(cmn.ReturnCodes):
    """Possible exit codes from this branch name checker."""

    SUCCESS = 0
    MAIN = 0
    INVALID_BRANCH = 1
    ERROR = 2


def _check_branch_name_validity(branch_name: str) -> int:
    """
    Checks the branch name and handles the following cases by outputting and
    setting an error code:
    - valid
    - still on main
    - invalid (non-main)
    """

    if re.fullmatch(r"GA\d+\.[A-Za-z0-9-_.]+", branch_name):
        rc = _BranchNameReturnCodes.SUCCESS
        print(
            "Branch name is valid. "
            "Make sure the branch is attached to an issue."
        )
    elif branch_name == "main":
        rc = _BranchNameReturnCodes.MAIN
        print(
            "Still on `main`. Move your changes to a new branch by doing:\n"
            "    `git checkout -b <new-branch>"
        )
    else:
        rc = _BranchNameReturnCodes.INVALID_BRANCH
        print(
            "Branch name is invalid. Branch name must be of the format:\n"
            "    GA<issue number>.<hyphenated-description-of-issue>\n"
        )
        print(
            "Permitted characters in the description are:\n"
            "- Alphanumeric characters\n"
            "- Hyphen (-)\n"
            "- Underscore (_)\n"
            "- Full stop (.)\n"
        )
        print("Resolve by doing the following:")
        print("    1. `git branch -m <new-branch>`")
        print("    2. `git push origin --delete <old-branch>`")
        print("    3. `git push origin -u <new-branch>`")

    return rc


def _get_current_branch() -> str:
    """
    Queries git to get the current branch name.

    :return:
        The current branch name
    """
    cmd = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
    try:
        output = subprocess.run(cmd, capture_output=True, check=True)
    except Exception:
        print("\nERROR")
        print(f"Exception raised running `{' '.join(cmd)}`:")
        raise
    branch_name = output.stdout.decode("utf-8").strip("\n")
    return branch_name


def main() -> None:
    """Main function to check that the working branch has a valid name."""
    branch_name = _get_current_branch()
    rc = _check_branch_name_validity(branch_name)

    sys.exit(rc)


if __name__ == "__main__":
    main()
