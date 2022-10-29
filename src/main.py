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

    parser.add_argument(
        "-s",
        "--suppress-output",
        action="store_true",
        help="Suppress logging output",
    )

    composition = parser.add_subparsers(dest="composition")

    # Hukamnama
    hukamnama = composition.add_parser(
        "hukamnama",
        description="Data regarding hukamnama archives.",
    )

    hukamnama_subparser = hukamnama.add_subparsers(dest="function")

    ## Data
    data = hukamnama_subparser.add_parser(
        _hukamnama.Function.DATA.value,
        description="Update database from archives."
    )
    data.add_argument(
        "-u",
        "--update",
        action="store_const",
        const=_hukamnama.DataUpdate.UPDATE,
        dest="update",
        help="Ensure database contains information from dates from the most recent recorded, up to today.",
    )
    data.add_argument(
        "-U",
        "--update-fill-gaps",
        action="store_const",
        const=_hukamnama.DataUpdate.UPDATE_FILL_GAPS,
        dest="update",
        help="Update database and attempt to fill in any gaps.",
    )
    data.add_argument(
        "-o",
        "--overwrite",
        action="store_const",
        const=_hukamnama.DataUpdate.OVERWRITE,
        dest="update",
        help="Starting from the beginning of the database, repopulate all data.",
    )

    args = parser.parse_args()
    print(args)

    if rc.is_ok():
        subparser = None
        if args.composition == "hukamnama":
            subparser = _hukamnama

        if subparser is not None:
            rc = subparser.parse(args)

    sys.exit(rc)


if __name__ == "__main__":
    main()
