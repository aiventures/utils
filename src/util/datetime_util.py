"""Calendar and Time Utils"""

import logging
import os
import re
from datetime import date, timedelta
from datetime import datetime as DateTime
from enum import StrEnum
from math import ceil
from typing import Dict

import pytz
from dateutil.parser import parse
from dateutil.tz import tzoffset, tzutc

from model.model_calendar import (
    CalendarIndexType,
)
from model.model_worklog import ShortCodes

# regex to extract todo_txt string matching signature @(...)
from util import constants as C

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))

DAYS_IN_MONTH = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
WEEKDAY = {1: "Mo", 2: "Di", 3: "Mi", 4: "Do", 5: "Fr", 6: "Sa", 7: "So"}
WEEKDAY_EN = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}
# WORKDAYS = ["onduty","workday","workday_home"]

MONTHS = {
    1: "Januar",
    2: "Februar",
    3: "März",
    4: "April",
    5: "Mai",
    6: "Juni",
    7: "Juli",
    8: "August",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Dezember",
}

MONTHS_EN = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


MONTHS_SHORT = {
    1: "JAN",
    2: "FEB",
    3: "MRZ",
    4: "APR",
    5: "MAI",
    6: "JUN",
    7: "JUL",
    8: "AUG",
    9: "SEP",
    10: "OKT",
    11: "NOV",
    12: "DEZ",
}

MONTHS_SHORT_EN = {
    1: "JAN",
    2: "FEB",
    3: "MAR",
    4: "APR",
    5: "MAY",
    6: "JUN",
    7: "JUL",
    8: "AUG",
    9: "SEP",
    10: "OCT",
    11: "NOV",
    12: "DEC",
}

# Patterns for Date Identification
# regex match any 8 Digit Groups preceded by space or start of line
# and not followed by a dash
# REGEX_YYYYMMDD = re.compile(r"((?<=\s)|(?<=^))(\d{8})(?!-)")
# REGEX_DATE_RANGE = re.compile(r"\d{8}-\d{8}")
REGEX_TIME_RANGE = re.compile(r"\s(\d{4}-\d{4})")
# any combination of Upper/Lowercase String  in German
# REGEX_WEEKDAY = re.compile(r"[MDFS][oira]")
# REGEX TO Extract a TODO.TXT substring
# REGEX_TODO_TXT = r"@[Tt]\((.+)?\)"
# REGEX_TODO_TXT_REPLACE = r"@[Tt]\(.+?\)"
# REGEX for TAGS / excluding the TODOO TXT tag
# REGEX_TAGS = r"@([^Tt][a-zA-Z0-9_]+)"
# REGEX_TAGS_REPLACE = r"@[^Tt][a-zA-Z0-9_]+"

# REGEX FOR TOTAL WORK
# REGEX_TOTAL_WORK = r"@TOTALWORK([0-9,.]+)"
# REGEX_TOTAL_WORK_REPLACE = r"@TOTALWORK[0-9,.]+"


class DateTimeUtil:
    """Util Functions for Date and Time"""

    @staticmethod
    def duration_from_str(s: str, as_str: bool = False) -> float | str:
        """Calculates Durations from hhMM-HHMM strings in hours or as time string
        also sums up multiple occurences
        """
        _durations = re.findall(REGEX_TIME_RANGE, s)
        if len(_durations) == 0:
            return None

        _total_duration = 0.0
        for _duration in _durations:
            try:
                _from, _to = [DateTime.strptime(_t, "%H%M") for _t in _duration.split("-")]
                # duration in minutes
                _total_duration += (_to - _from).seconds // 60
            except ValueError as e:
                logger.warning(f"[DateTimeUtil] Couldn't Parse [{s}] as DateTime Object, {e}")
        _hours = round(float(_total_duration) / 60, 2)
        # no durations found return None
        if _hours == 0.0:
            return None
        if as_str:
            _hours_s = str(int(_hours // 1)).zfill(2)
            _minutes_s = str(round((_hours % 1) * 60)).zfill(2)
            _hours = f"{_hours_s}:{_minutes_s}"
        return _hours

    @staticmethod
    def get_datetime_from_string(datetime_s: str, local_tz="Europe/Berlin") -> DateTime:
        """returns datetime for date string with timezone
        allowed formats:  ####:##:## ##:##:##  (datetime localized with local_tz)
                          ####-##-##T##:##:##Z  (UTC)
                          ####-##-##T##:##:##.000Z
                          ####-##-##T##:##:##(+/-)##:## (UTC TIme Zone Offsets)

        (<year>-<month>-<day>T<hour>-<minute>(T/<+/-time offset)
        """
        dt = None

        datetime_s_in = datetime_s[:]

        reg_expr_utc = "\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$"
        reg_expr_dt = "\\d{4}[:-]\\d{2}[:-]\\d{2} \\d{2}[:-]\\d{2}[:-]\\d{2}"

        reg_expr_utc2 = "\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}[.]000Z$"
        reg_expr_tz = "\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}[+-]\\d{2}:\\d{2}$"

        if len(re.findall(reg_expr_dt, datetime_s)) == 1:  # date time format
            try:
                timezone_loc = pytz.timezone(local_tz)
                dt_s = (
                    datetime_s[0:4]
                    + "-"
                    + datetime_s[5:7]
                    + "-"
                    + datetime_s[8:10]
                    + " "
                    + datetime_s[11:13]
                    + "-"
                    + datetime_s[14:16]
                    + "-"
                    + datetime_s[17:19]
                )
                dt = DateTime.strptime(dt_s, "%Y-%m-%d %H-%M-%S")
                dt = timezone_loc.localize(dt)  # abstain from datetime.replace :-) ...
            except:
                return 0

        elif len(re.findall(reg_expr_utc2, datetime_s)) == 1:  # utc2 format
            datetime_s = datetime_s[:-5] + "+00:00"
        elif len(re.findall(reg_expr_utc, datetime_s)) == 1:  # utc format
            datetime_s = datetime_s[:-1] + "+00:00"
        elif len(re.findall(reg_expr_tz, datetime_s)) == 1:  # time zone format
            pass  # this time zone already has the correct format
        else:
            logger.warning(f"can't evaluate time format {datetime_s} ")
            return 0

        if dt is None:
            # omit colon
            try:
                dt_s = datetime_s[:-3] + datetime_s[-2:]
                dt = DateTime.strptime(dt_s, "%Y-%m-%dT%H:%M:%S%z")
            except:
                return None

        logger.debug(
            f"[DateTimeUtil] IN:{datetime_s_in}, dt:{dt}, tz:{dt.tzinfo} utc:{dt.utcoffset()}, dst:{dt.tzinfo.dst(dt)}"
        )

        return dt

    @staticmethod
    def add_shortcodes(shortcode_dict: dict) -> StrEnum:
        """adding shortcodes to standard worklog enum codes"""
        # create a Dict
        _shortcode_dict = {_code.name: _code.value for _code in ShortCodes}
        # add shortcodes
        _shortcode_dict.update(shortcode_dict)
        return StrEnum("ShortCodes", _shortcode_dict)

    @staticmethod
    def get_timestamp(datetime_s: str, local_tz="Europe/Berlin") -> int:
        """returns UTC timestamp for date string"""

        dt = DateTimeUtil.get_datetime_from_string(datetime_s, local_tz)
        ts = int(dt.timestamp())
        logger.debug(f"[DateTimeUtil] Datestring: {datetime_s} Timezone {local_tz} Timestamp: {ts}")

        return ts

    @staticmethod
    def get_time_offset(time_device: str, time_gps: str) -> timedelta:
        """helps to calculate offset due to difference of GPS Logger and Device Time Difference
        difference = time(gps) - time(device) > time(gps) = time(device) + difference
        returns a timedelta object
        """
        try:
            ts_gps = DateTime.fromtimestamp(DateTimeUtil.get_timestamp(time_gps))
            ts_cam = DateTime.fromtimestamp(DateTimeUtil.get_timestamp(time_device))
        except:
            raise Exception(f"GPS Timestamp {time_gps} or Camera Timestamp {time_device} not correct")

        delta_time = ts_gps - ts_cam

        logger.debug(
            f"[DateTimeUtil] GPS:{time_gps} - Camera:{time_device} = Time Offset:{(delta_time//timedelta(seconds=1))}"
        )

        return delta_time

    @staticmethod
    def get_localized_datetime(dt_in, tz_in="Europe/Berlin", tz_out="UTC", as_timestamp=False) -> DateTime:
        """helper method to get non naive datetime (based on input and output timezone),
        input date can be string or datetime,
        timezone can be string or pytz object, optionally returns also as utc timestamp"""

        reg_expr_datetime = "\\d{4}[-:]\\d{2}[:-]\\d{2} \\d{2}[:-]\\d{2}[:-]\\d{2}"

        def get_tz_info(tz):
            if isinstance(tz, pytz.BaseTzInfo):
                tz_info = tz
            elif isinstance(tz_in, str):
                tz_info = pytz.timezone(tz)
            else:
                tz_info = pytz.timezone("UTC")
            return tz_info

        if dt_in is None:
            return None

        tz_utc = pytz.timezone("UTC")
        pytz_in = get_tz_info(tz_in)
        pytz_out = get_tz_info(tz_out)

        if isinstance(dt_in, DateTime):
            dt = dt_in
        elif isinstance(dt_in, str):
            # convert date hyphens
            if len(re.findall(reg_expr_datetime, dt_in)) == 1:
                dt_in = dt_in[:10].replace(":", "-") + dt_in[10:]

            # utc code
            if dt_in[-1] == "Z":
                dt_in = dt_in[:-1] + "+00:00"
            dt = parse(dt_in)

        dt = None
        tz_info = dt.tzinfo

        # naive datetime, convert to input timezone
        if tz_info is None:
            dt = pytz_in.localize(dt)
            tz_info = dt.tzinfo

        # convert to utc time formats
        if (isinstance(tz_info, tzutc)) or (isinstance(tz_info, tzoffset)):
            dt_utc = dt.astimezone(tz_utc)
        else:
            dt_utc = tz_utc.normalize(dt)

        # convert to target timezone
        if as_timestamp:
            out = int(dt_utc.timestamp())
        else:
            out = dt_utc.astimezone(pytz_out)

        logger.debug(f"[DateTimeUtil] date IN: {dt_in} -> datetime {dt} ({pytz_in})")
        logger.debug(f"[DateTimeUtil]   -> UTC datetime {dt_utc} -> datetime {out} ({pytz_out})")
        logger.debug(
            f"[DateTimeUtil]   -> Timestamp {dt_utc.timestamp()} with UTC datetime {DateTime.utcfromtimestamp(dt_utc.timestamp())}"
        )
        return out

    @staticmethod
    def get_easter_sunday(year: int, verbose=False) -> DateTime | dict:
        """Calculates easter sunday
        Arguments
        year: Year
        verbose: if true returns a detailed dictionary of calculations date object otherwise
        showinfo: show information
        Returns: Date or Info Dictionary of Easter Sunday
        Reference: https://www.tondering.dk/claus/cal/easter.php
        """
        G = (year % 19) + 1
        epact_julian = (11 * (G - 1)) % 30  # epact in julian calendar
        C = (year // 100) + 1  # century
        S = (3 * C) // 4  # solar equation, difference Julian vs. Gregorian
        L = (8 * C + 5) // 25  # Lunar Equation, difference between the Julian calendar and the Metonic cycle.

        # Gregorian EPact
        # The number 8 is a constant that calibrates the starting point of the Gregorian Epact so
        # that it matches the actual age of the moon on new year’s day.
        epact_gregorian = epact_julian - S + L + 8

        # adjust so that gregorian epact is within range of 1 to 30
        if epact_gregorian == 0:
            epact_gregorian = 30
        elif (epact_gregorian > 30) or (epact_gregorian < 0):
            epact_gregorian = epact_gregorian % 30

        # now calculate paschal full moon
        if epact_gregorian < 24:
            d_fm = date(year, 4, 12)
            d_offset = epact_gregorian - 1
        else:
            d_fm = date(year, 4, 18)
            d_offset = epact_gregorian % 24
            if epact_gregorian > 25:
                d_offset -= 1
            # April 18 otherwise April 17
            elif (epact_gregorian == 25) and (G < 11):
                d_offset -= 1

        d_fm = d_fm - timedelta(days=d_offset)
        d_weekday = d_fm.isoweekday()

        # offset calculate nex sunday / in case its a sunday it will be follow up sunday
        d_e_offset = 7 - (d_weekday % 7)
        d_easter = d_fm + timedelta(days=d_e_offset)
        logger.debug(
            f" {year}|G:{str(G).zfill(2)} Epact:{str(epact_gregorian).zfill(2)}|C:{C} S:{S} L:{L}"
            + f"|F.Moon {d_fm}-{d_fm.strftime('%a')}|Eastern {d_easter}/{d_easter.strftime('%a')}|"
        )

        # Return Easter Sunday either as date only or as detailed dictionary
        if verbose:
            d_easter_dict = {}
            d_easter_dict["golden_number"] = G
            d_easter_dict["epact_julian"] = epact_julian
            d_easter_dict["century"] = C
            d_easter_dict["solar_equation"] = S
            d_easter_dict["lunar_equation"] = L
            d_easter_dict["epact_gregorian"] = epact_gregorian
            d_easter_dict["date_full_moon"] = d_fm
            d_easter_dict["isoweekday_full_moon"] = d_weekday
            d_easter_dict["date_eastern"] = d_easter
            return d_easter_dict
        else:
            return d_easter

    @staticmethod
    def get_holiday_dates(year: int, show_info=False) -> dict:
        """Calculates holiday dates for Baden Württemberg for given year"""

        holiday_list = {
            "Neujahr": {"month": 1, "day": 1, "holiday": 1},
            "Dreikönig": {"month": 1, "day": 6, "holiday": 1},
            "Rosenmontag": {"holiday": 0, "offset": -48},
            "Aschermittwoch": {"holiday": 0, "offset": -46},
            "Karfreitag": {"holiday": 1, "offset": -2},
            "Ostersonntag": {"holiday": 0, "offset": 0},
            "Ostermontag": {"holiday": 1, "offset": 1},
            "1.Mai": {"month": 5, "day": 1, "holiday": 1},
            "Himmelfahrt": {"holiday": 1, "offset": 39},
            "Pfingstsonntag": {"holiday": 0, "offset": 49},
            "Pfingstmontag": {"holiday": 1, "offset": 50},
            "Fronleichnam": {"holiday": 1, "offset": 60},
            "Dt Einheit": {"month": 10, "day": 3, "holiday": 1},
            "Allerheiligen": {"month": 11, "day": 1, "holiday": 1},
            "Heiligabend": {"month": 12, "day": 24, "holiday": 1},
            "1.Weihnachtstag": {"month": 12, "day": 25, "holiday": 1},
            "2.Weihnachtstag": {"month": 12, "day": 26, "holiday": 1},
            "Silvester": {"month": 12, "day": 31, "holiday": 1},
        }

        d_easter = DateTimeUtil.get_easter_sunday(year)

        out_dict = {}
        num_holidays = 0

        if show_info:
            print(f"\n--- Holiday Days for year {year} ---")

        for h, v in holiday_list.items():
            # check if it is a fixed holiday
            offset = holiday_list[h].get("offset", None)
            if offset is None:
                d_holiday = DateTime(year, v["month"], v["day"])
            else:
                d_holiday = d_easter + timedelta(days=v["offset"])
            d_holiday = DateTime(d_holiday.year, d_holiday.month, d_holiday.day)

            weekday = d_holiday.isoweekday()
            v["weekday"] = weekday
            v["year"] = year
            v["d"] = DateTime(d_holiday.year, d_holiday.month, d_holiday.day)
            v["name"] = h
            if weekday >= 6:
                v["holiday"] = 0
            out_dict[d_holiday] = v

            if show_info:
                num_holidays += v["holiday"]
                print(f"{d_holiday.strftime('%Y-%B-%d (%A)')}: {h} ({v['holiday']})")
        if show_info:
            print(f"--- Number of Holiday Days {year}: {num_holidays} ---")

        return out_dict

    @staticmethod
    def is_leap_year(y) -> bool:
        """check whether year is leap year"""
        ly = False

        if (y % 4 == 0) and not y % 100 == 0:
            ly = True

        if (y % 100 == 0) and not y % 400 == 0:
            ly = False

        if y % 400 == 0:
            ly = True

        return ly

    @staticmethod
    def get_1st_isoweek_date(y: int) -> DateTime:
        """returns monday date of first isoweek of a given calendar year
        https://en.wikipedia.org/wiki/ISO_week_date
        W01 is the week containing 1st Thursday of the Year
        """
        d_jan1 = date(y, 1, 1)
        wd_jan1 = d_jan1.isoweekday()
        # get the monday thats in the week of JAN 1
        d_monday_jan1 = d_jan1 - timedelta(days=wd_jan1 - 1)
        # number of days of this week that is in the new year
        _num_days_new_year = 7 - (d_jan1 - d_monday_jan1).days
        # majority of days (4) in new calendar week = nothing to do we have the new monday
        # if majority of days in old year (<=3), then it is next monday
        if _num_days_new_year <= 3:
            d_monday_jan1 += timedelta(days=7)
        dt_monday_w01 = DateTime(d_monday_jan1.year, d_monday_jan1.month, d_monday_jan1.day)

        return dt_monday_w01

    @staticmethod
    def get_isoweekyear(y: int) -> dict:
        """returns isoweek properties for given calendar year as dictionary:
        1st and last monday of isoweek year, number of working weeks
        """
        d_first = DateTimeUtil.get_1st_isoweek_date(y)
        d_last = DateTimeUtil.get_1st_isoweek_date(y + 1)
        working_weeks = (d_last - d_first).days // 7
        d_last = DateTimeUtil.get_1st_isoweek_date(y + 1) - timedelta(days=7)
        isoweekyear = {}
        isoweekyear["first_monday"] = d_first
        isoweekyear["last_monday"] = d_last
        isoweekyear["last_day"] = d_last + timedelta(days=6)
        isoweekyear["weeks"] = working_weeks
        isoweekyear["year"] = y

        return isoweekyear

    @staticmethod
    def isoweek(d: DateTime):
        """ " returns isoweek (isoweek,calendar year,number of passed days in calendar year) for given date"""
        y = d.year

        wy = DateTimeUtil.get_isoweekyear(y)

        # check if date is in boundary of current calendar year
        if d < wy["first_monday"]:
            wy = DateTimeUtil.get_isoweekyear(y - 1)
        elif d > wy["last_day"]:
            wy = DateTimeUtil.get_isoweekyear(y + 1)

        iso = {}
        iso["year"] = wy["year"]
        iso["leap_year"] = DateTimeUtil.is_leap_year(wy["year"])
        iso["weeks_year"] = wy["weeks"]
        iso["day_in_year"] = (d - wy["first_monday"]).days + 1
        iso["calendar_week"] = ceil(iso["day_in_year"] / 7)
        iso["weekday"] = d.isoweekday()
        return iso

    @staticmethod
    def year_index(year: int = None) -> Dict[int, CalendarIndexType]:
        """creates a year index pointing to month, day tuple and isoweek infos"""
        out = {}
        _idx = 1
        if year is None:
            year = DateTime.now().year
        _holidays = DateTimeUtil.get_holiday_dates(year)
        curr_year = year
        curr_date = DateTime(year, 1, 1)
        while year == curr_year:
            _is_holiday = False
            _holiday = _holidays.get(curr_date)
            if _holiday:
                _is_holiday = True
                _holiday = _holiday["name"]
            _info = DateTimeUtil.isoweek(curr_date)
            _weekday = _info["weekday"]
            _is_workday = True
            _is_weekend = False
            if _weekday > 5:
                _is_workday = False
                _is_weekend = True
            _idx_info = {
                "datetime": curr_date,
                "year": _info["year"],
                "month": curr_date.month,
                "day": curr_date.day,
                "day_in_year": _idx,
                "calendar_week": _info["calendar_week"],
                "month_day": [curr_date.month, curr_date.day],
                "weekday": _info["weekday"],
                "holiday": _holiday,
                "is_leap_year": _info["leap_year"],
                "is_holiday": _is_holiday,
                "is_weekend": _is_weekend,
                "is_workday": _is_workday,
            }
            out[_idx] = CalendarIndexType(**_idx_info)
            curr_date += timedelta(days=1)
            curr_year = curr_date.year
            _idx += 1
        return out

    @staticmethod
    def get_dates_from_range(daterange: str) -> list:
        """Transforms a string of format yyyymmdd-YYYYMMDD into a list of dates"""
        out = []
        _date_from, _date_to = [DateTime.strptime(_d, "%Y%m%d") for _d in daterange.split("-")]
        _date = _date_from
        while _date <= _date_to:
            out.append(_date)
            _date = _date + timedelta(days=1)
        return out
