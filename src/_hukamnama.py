# ------------------------------------------------------------------------------
# main.py - Hukamnama parsing
#
# October 2022, Gurkiran Singh
#
# Copyright (c) 2022
# All rights reserved.
# ------------------------------------------------------------------------------

"""Parses requests for hukamnama parsing."""

__all__ = [
    "DataUpdate",
    "Function",
    "parse",
]

from dataclasses import dataclass
from urllib.request import Request, urlopen

import datetime
import enum

_DATE_FORMAT = '%Y-%m-%d'
_FIRST_DATE = "2002-01-01"
_today_date = datetime.datetime.today().strftime(_DATE_FORMAT)

_BASE_URL = "https://www.sikhnet.com/hukam/archive/"

class DataUpdate(enum.IntEnum):
    """
    Methods of updating data in the database.

    WRITE: Starting from the beginning of the archives, (re)populate all entries
        until today (overwrites existing data)
    UPDATE: Add information to database, continuing from the most recently
        populated entry, until today
    UPDATE_FILL_GAPS: Starting from the beginning of the archives, populate
        entries without any data (does not overwrites existing data)
    """
    UNKNOWN = 0
    WRITE = 1
    UPDATE = 2
    UPDATE_FILL_GAPS = 3

class Function(enum.Enum):
    """
    Subfunctions within Hukamnama Analysis.

    DATA: Update/repopulate the database
    """
    DATA = "data"

@dataclass(frozen=True)
class _ShabadMetaData:
    """Object to store information about each shabad recorded."""
    url: str
    ang: int
    gurmukhi: list
    raag: str
    writer: str
    first_letter_gurmukhi: str
    first_letter_english: str

def _data(ctx):
    """
    Handler for all data requests to the Hukamnama CLI.

    :param ctx:
        Context about the original instruction.
    """
    print(":\n")
    if ctx.verbosity.is_very_verbose():
        print(
            "Ignoring today's shabad:\n  - ",
            "\n ".join(_get_today_hukam(ctx).gurmukhi)
        )
    if ctx.update is DataUpdate.WRITE:
        start = _FIRST_DATE
        end = _today_date
    elif ctx.update is DataUpdate.UPDATE:
        pass
    elif ctx.update is DataUpdate.UPDATE_FILL_GAPS:
        pass
    else:
        raise NotImplementedError # FAIL_COMMIT

    if ctx.verbosity.is_verbose():
        print(f"Operating between dates: {start} - {end}")

    start_date_split = start.split("-")
    prev_year = start_date_split[0]
    prev_month = start_date_split[1]

    for date in _get_next_date(start, end):
        date_split = date.split("-")
        current_year = date_split[0]
        current_month = date_split[1]
        if current_month != prev_month:
            if current_year != prev_year:
                prev_year = current_year
                if not ctx.verbosity.is_suppressed():
                    print("  new year: ", current_year)
            prev_month = current_month
            if not ctx.verbosity.is_suppressed():
                print("  new month: ", current_month)
        url = _BASE_URL + date
        try:
            shabad = _scrape(ctx, url)
            print(shabad)
        except:
            raise # FAIL_COMMIT

def _get_ang(html):
    """
    Scrapes the ang of the hukamnama from the HTML.

    :param html:
        Full HTML source code.

    :return:
        The ang corresponding to the hukamnama.
    """
    ang_start = html.split('"angs":{"')[1]
    ang = int(ang_start.split('"')[0])
    return ang

def _get_first_letter(first_line):
    """
    FAIL_COMMIT TODO

    :param first_line: _description_
    :return: _description_
    """
    if first_line[0] == "i": # sihaari
        return first_line[1]
    else:
        return first_line[0]

def _get_next_date(start, end):
    """
    Generates dates between the given start and end dates (inclusive) in order.
    Dates must be in YYYY-MM-DD format.

    :param start:
        Date to begin range with.

    :param end:
        Date to end range with.
    """
    start_date = datetime.datetime.strptime(start, _DATE_FORMAT)
    end_date = datetime.datetime.strptime(end, _DATE_FORMAT)
    difference = (end_date - start_date).days + 1
    for x in range(0, difference):
        yield str(start_date + datetime.timedelta(days=x)).split(" ")[0]

def _get_today_hukam(ctx):
    """
    Get today's hukamnama.

    :param ctx:
        Context about the original instruction.

    :return:
        _ShabadMetaData object corresponding to today's hukamnama
    """
    return _scrape(ctx, _BASE_URL+_today_date)

def _gurbani_ascii_to_unicode(letter):
    """
    FAIL_COMMIT TODO

    :param letter: _description_
    :return: _description_
    """
    mapping = {
        "a": "ੳ",
        "A": "ਅ",
        "e": "ੲ",
        "s": "ਸ",
        "h": "ਹ",
        "k": "ਕ",
        "K": "ਖ",
        "g": "ਗ",
        "G": "ਘ",
        "|": "ਙ",
        "c": "ਚ",
        "C": "ਛ",
        "j": "ਜ",
        "J": "ਝ",
        "|": "ਞ",
        "t": "ਟ",
        "T": "ਠ",
        "f": "ਡ",
        "F": "ਢ",
        "x": "ਣ",
        "q": "ਤ",
        "Q": "ਥ",
        "d": "ਦ",
        "D": "ਧ",
        "n": "ਨ",
        "p": "ਪ",
        "P": "ਫ",
        "b": "ਬ",
        "B": "ਭ",
        "m": "ਮ",
        "X": "ਯ",
        "r": "ਰ",
        "l": "ਲ",
        "v": "ਵ",
        "V": "ੜ",
    }
    return mapping[letter]

def _load_webpage_data(url):
    """
    FAIL_COMMIT TODO

    :param url: _description_
    :return: _description_
    """
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req)
    html = page.read().decode("utf-8")
    return html

def parse(ctx):
    """
    FAIL_COMMIT TODO

    :param ctx: _description_
    """
    if ctx.verbosity.is_very_verbose():
        print("Setting today's date as", _today_date)

    if ctx.function == Function.DATA.value:
        _data(ctx)
    else:
        raise NotImplementedError # FAIL_COMMIT



    # try:
    #     for date in date_generated:
    #         current_year = str(date)[:4]
    #         current_month = str(date)[5:7]
    #         url = base_url + str(date)[:10]
    #         try:
    #             ang, letter = scrape(url)
    #             if letter_frequencies[letter] == 0:
    #                 print(ang, letter)
    #             angs.append(ang)
    #             if letter == "E":
    #                 letter = "a" # assign oora nu horaa to oora
    #             letter_frequencies[letter] += 1
    #         except TypeError as e: # ignore this hukamnama
    #             pass # print(str(e))
    #         except KeyError:
    #             print(str(e))
    #         except KeyboardInterrupt:
    #             raise KeyboardInterrupt
    #         except:
    #             print("Server error:", url)



def _remove_manglacharan(ctx, shabad_lines):
    """FAIL_COMMIT TODO

    :param ctx: _description_
    :param shabad_lines: _description_
    :return: _description_
    """
    # characters and phrases exclusive to manglacharans:
    mangals = ["\\u003C\\u003E", " siqgur pRswid ]",
         " 1", " 2", " 3", " 4", " 5", " 9",
         "slok m", "slok ]", "sloku m", "sloku ]", "pauVI",
         "sUhI", "iblwvlu", "jYqsrI", "soriT", "DnwsrI", "dyvgMDwrI", "Awsw ]",
         "goNf",

         " kbIr jI", "nwmdyv jI", "bwxI Bgqw "]

    while True:
        if shabad_lines[0] in mangals:
            if ctx.verbosity.is_very_verbose():
                print("  Removing manglacharan", shabad_lines[0])
            shabad_lines.pop(0)
        else:
            break
    return shabad_lines

def _scrape(ctx, url):
    """
    FAIL_COMMIT TODO

    :param url: _description_
    :return:
    """
    if ctx.verbosity.is_verbose():
        print("Scraping data from", url)
    html = _load_webpage_data(url)

    ang = _get_ang(html)
    if ctx.verbosity.is_verbose():
        print(" - Ang is", ang)

    shabad_lines = _separate_lines(html)
    if ctx.verbosity.is_very_verbose():
        print(
            " - Shabad is:\n  - ",
            "\n    ".join(shabad_lines)
        )

    first_line = _remove_manglacharan(ctx, shabad_lines)[0]
    if ctx.verbosity.is_verbose():
        print(" - First line is", first_line)

    first_letter_gurmukhi = _get_first_letter(first_line)
    if ctx.verbosity.is_verbose():
        print(
            " - First letter is",
            first_letter_gurmukhi,
            f"({_gurbani_ascii_to_unicode(first_letter_gurmukhi)})"
        )

    return _ShabadMetaData(
        url=url,
        ang=ang,
        gurmukhi=shabad_lines,
        raag="FAIL_COMMIT",
        writer="FAIL_COMMIT",
        first_letter_gurmukhi=first_letter_gurmukhi,
        first_letter_english="FAIL_COMMIT",
    )

def _separate_lines(html):
    """FAIL_COMMIT TODO

    :param html: _description_
    :return: _description_
    """
    shabad_start = html.split('shabad_lines":{"gurmukhi":["')[1]
    shabad = shabad_start.split('"],"transliteration')[0]
    shabad_lines = shabad.split('","')
    return shabad_lines
