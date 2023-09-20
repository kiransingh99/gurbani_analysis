# ------------------------------------------------------------------------------
# _ardaas.py - Ardaas generator
#
# June 2023, Gurkiran Singh
#
# Copyright (c) 2023
# All rights reserved.
# ------------------------------------------------------------------------------

"""Handler for ardaas subparser."""

from __future__ import annotations

__all__ = ["Function", "parse"]

import argparse

import _cmn

_log = _cmn.Logger("ardaas")


def _generate(ctx: argparse.Namespace) -> None:
    """Handler for all generate requests to the Ardaas CLI.

    :param ctx: context about the original instruction.
    """
    start_unicode = ["Awp jI dy hzUr Ardws byNqI jodVI hY"]
    end_unicode = [
        "A~Kr vwDw Gwtw Bul cuk mwP krnI",
        "srb~q dy kwrj rws krny",
        "seI ipAwry myl ijnHW imilAW qyrw nwm icq Awvy",
        "nwnk nwm cVHdI klw",
        "qyry Bwny srb~q dw Blw",
    ]

    ardaas_unicode = []

    if ctx.hukamnama:
        ardaas_unicode.extend(_hukamnama(ctx.multiple))

    ardaas_unicode = start_unicode + ardaas_unicode + end_unicode + ["["]
    ardaas = "[ ".join(ardaas_unicode)

    # Now that the ardaas is fully generated, translate it
    if ctx.romanised:
        ardaas = _translate_to_romanised(ardaas)
    # if ctx.ascii:
    #     ascii = _translate_to_ascii(ardaas_unicode)

    print(ardaas)


def _hukamnama(multiple):
    jagat_jalandhaa = "jgqu jlµdw riK lY AwpxI ikrpw Dwir ]\
ijqu duAwrY aubrY iqqY lYhu aubwir ]\
siqguir suKu vyKwilAw scw sbdu bIcwir ]\
nwnk Avru n suJeI hir ibnu bKsxhwru ]"

    hukamanama_benti = f"dws{'W' if multiple else ''} nUM awp jI dw pwvn pivqr hukmnwmw bKSo jI"

    return [jagat_jalandhaa, hukamanama_benti]


def parse(ctx: argparse.Namespace) -> None:
    """Main handler for Ardaas CLI. This is the API called by the main
    Gurbani Analysis CLI.

    :param ctx: context received from the Gurbani Analysis CLI. Namespace object
        containing the args received by the CLI.
    """
    _log.set_level(ctx.verbosity)
    _generate(ctx)

    return _cmn.RC.SUCCESS


def _translate_to_romanised(unicode):
    romanised = _cmn.gurbani_unicode_to_romanised(unicode)

    return romanised
