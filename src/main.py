# ------------------------------------------------------------------------------
# main.py - Main handler for Gurbani Analysis CLI
#
# October 2022, Gurkiran Singh
#
# Copyright (c) 2022
# All rights reserved.
# ------------------------------------------------------------------------------

"""Main handler for Gurbani Analysis CLI."""

__all__ = []

import argparse
import sys

import cmn
import _hukamnama


def main():
    """
    FAIL_COMMIT TODO
    """

    rc = cmn.RC.SUCCESS

    parser = argparse.ArgumentParser(
        description="Collect and analyse data about Gurbani."
    )

    composition = parser.add_mutually_exclusive_group()

    composition.add_argument(
        "-H",
        "--hukamnama",
        action="store_true",
        default=False,
        help="Analyse data from the archive of hukamnamas from Harmandir Sahib.",
    )

    args, remainder = parser.parse_known_args()

    if rc.is_ok():
        subparser = None
        if args.hukamnama:
            subparser = _hukamnama

        if subparser is not None:
            rc = subparser._parse(*remainder)

    sys.exit(rc)


if __name__ == "__main__":
    main()
