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
    start_unicode = ["Awp jI dy hzUr Ardws byNqI jodVI hY[ "]
    end_unicode = [
        "A~Kr vwDw Gwtw Bul cuk mwP krnI[ ",
        "srb~q dy kwrj rws krny[ ",
        "seI ipAwry myl ijnHW imilAW qyrw nwm icq Awvy[ ",
        "nwnk nwm cVHdI klw[ ",
        "qyry Bwny srb~q dw Blw[ ",
    ]

    ardaas_unicode = []

    if ctx.sukhmani:
        ardaas_unicode.extend(_sukhmani())
    # For any banis that were read:
    if ctx.sukhmani:
        ardaas_unicode.extend(_read_banis(ctx.multiple))
        # @@@ is bani da bhav is bani da ful sangata de hirde vich vasaona

    if ctx.hukamnama:
        ardaas_unicode.extend(_hukamnama(ctx.multiple))

    ardaas_unicode = start_unicode + ardaas_unicode + end_unicode + ["["]
    ardaas = "".join(ardaas_unicode)

    # Now that the ardaas is fully generated, translate it
    if ctx.romanised:
        ardaas = _cmn.gurbani_unicode_to_romanised(ardaas)

    print(ardaas)


def _hukamnama(multiple: bool) -> list[str]:
    """Add lines to the ardaas to state that a hukamnama was taken.

    :param multiple: set to True if multiple people are in the sangat.
    :return: list of lines to add to the ardaas.
    """
    jagat_jalandhaa = "jgqu jlµdw riK lY AwpxI ikrpw Dwir] \
ijqu duAwrY aubrY iqqY lYhu aubwir] \
siqguir suKu vyKwilAw scw sbdu bIcwir] \
nwnk Avru n suJeI hir ibnu bKsxhwru] "

    hukamanama_benti = (
        f"{_pluralise('dws', multiple)} nUM awp jI dw pwvn pivqr hukmnwmw bKSo jI[ "
    )

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


def _pluralise(word: str, plural: bool) -> str:
    """Take in a punjabi work and return the pluralised version of it, if
    `plural` is True. Else, return the original word.

    :param word: word to pluralise.
    :param plural: whether to pluralise the word or not.
    :return: pluralised word, if `plural` is True. Else, return the original
    """
    if not plural:
        return word

    special_cases = {}

    if word in special_cases:
        return special_cases[word]

    return word + "W"  # add kannaa


def _read_banis(multiple) -> list[str]:
    """Add lines to the ardaas to state that bani was read.

    :param multiple: set to True if multiple people are in the sangat.
    """
    return [
        f"{_pluralise('dws', multiple)} ny Awp jI dy crnw kmlw pws Su~D Aqy sp~St bwnI pVI, suxI Aqy ivcwr kIqIaw[ ",
        "bwnI pVHn, suxn Aqy ivcwr krn dy ivc AnkyW prkwr dIAw glqIAW hoieAw[ ",
        "Bul cu`k mwP krnI[ ",
    ]


def _sukhmani() -> list[str]:
    """Add lines to the ardaas to state that sukhmani sahib was read.

    :return: list of lines to add to the ardaas.
    """
    sukhmani = "suKmnI suK AMimRq pRB nwmu] \
Bgq jnw kY min ibsRwm] "

    sukhmani_ardaas = "suKmnI swihb dw jwp how[ "

    return [sukhmani, sukhmani_ardaas]
