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
        help="Analyse data from the archive of hukamnamas from Harmandir Sahib.",
    )

    subparsers = parser.add_subparsers()

    # Hukamnama
    hukamnama = subparsers.add_parser("hukam")

    hukamnama_subparser = hukamnama.add_subparsers()

    data = hukamnama_subparser.add_parser("data")
    data.add_argument(
        "-u",
        "--update",
        action="store_const",
        const=_hukamnama.DataUpdate.UPDATE,
        dest="update",
        help="Ensure database contains information from dates up to today."
    )
    data.add_argument(
        "-U",
        "--update-fill-gaps",
        action="store_const",
        const=_hukamnama.DataUpdate.UPDATE_FILL_GAPS,
        dest="update",
        help="Update database and attempt to fill in any gaps"
    )

    args = parser.parse_args()
    print(args)

    if rc.is_ok():
        subparser = None
        if args.hukamnama:
            subparser = _hukamnama

        if subparser is not None:
            rc = subparser._parse(*remainder)

    sys.exit(rc)


if __name__ == "__main__":
    main()
