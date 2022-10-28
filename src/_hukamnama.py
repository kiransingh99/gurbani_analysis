# ------------------------------------------------------------------------------
# main.py - Hukamnama parsing
#
# October 2022, Gurkiran Singh
#
# Copyright (c) 2022
# All rights reserved.
# ------------------------------------------------------------------------------

"""Parses requests for hukamnama parsing."""

__all__ = []

import enum


class DataUpdate(enum.IntEnum):
    """
    FAIL_COMMIT TODO
    """
    UNKNOWN = 0
    UPDATE = 1
    UPDATE_FILL_GAPS = 2
