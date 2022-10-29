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

import datetime
import enum

_DATE_FORMAT = '%Y-%m-%d'
_FIRST_DATE = "2002-01-01"
_TODAY_DATE = datetime.datetime.today().strftime(_DATE_FORMAT)

_BASE_URL = "https://www.sikhnet.com/hukam/archive/"


class DataUpdate(enum.IntEnum):
    """
    FAIL_COMMIT TODO
    """
    UNKNOWN = 0
    UPDATE = 1
    UPDATE_FILL_GAPS = 2
    OVERWRITE = 3

class Function(enum.Enum):
    """
    # FAIL_COMMIT
    """
    DATA = "data"

def _get_next_date(start, end):
    """
    FAIL_COMMIT TODO

    :param start: _description_
    :param end: _description_
    """
    start_date = datetime.datetime.strptime(start, _DATE_FORMAT)
    end_date = datetime.datetime.strptime(end, _DATE_FORMAT)
    for x in range(0, (
        end_date - start_date
    ).days+1):
        yield str(start_date + datetime.timedelta(days=x)).split(" ")[0]

def _data(args):
    """
    FAIL_COMMIT TODO

    :param args: _description_
    """
    if args.update is DataUpdate.UPDATE:
        pass
    elif args.update is DataUpdate.UPDATE_FILL_GAPS:
        pass
    elif args.update is DataUpdate.OVERWRITE:
        start = _FIRST_DATE
        end = _TODAY_DATE
    else:
        raise NotImplementedError # FAIL_COMMIT

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
                print("  new year: ", current_year)
            prev_month = current_month
            print("  new month: ", current_month)
        url = _BASE_URL + date
        print(url)

def parse(args):
    """
    FAIL_COMMIT TODO

    :param args: _description_
    """
    if args.function == Function.DATA.value:
        _data(args)
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


