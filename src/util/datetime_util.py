""" Calendar and Time Utils """

import logging
import os
import re
from datetime import date
from datetime import datetime as DateTime
from datetime import timedelta
from math import ceil
from typing import Dict

import pytz
from dateutil.parser import parse
from dateutil.tz import tzoffset, tzutc

from model.model_datetime import ( MonthModelType, CalendarDayType,
                                   YearModelType, DayTypeEnum,
                                   DayTypeListType )
from util import constants as C

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL,logging.INFO)))

DAYS_IN_MONTH = {1:31,2:28,3:31,4:30,5:31,6:30,
                 7:31,8:31,9:30,10:31,11:30,12:31}
WEEKDAY = {1:"Mo",2:"Di",3:"Mi",4:"Do",5:"Fr",6:"Sa",7:"So"}

MONTHS_SHORT = {1:"JAN",2:"FEB",3:"MRZ",
                4:"APR",5:"MAI",6:"JUN",
                7:"JUL",8:"AUG",9:"SEP",
                10:"OKT",11:"NOV",12:"DEZ"}

# Patterns for Date Identification
# regex match any 8 Digit Groups preceded by space or start of line
# and not followed by a dash
REGEX_YYYYMMDD = re.compile(r"((?<=\s)|(?<=^))(\d{8})(?!-)")
REGEX_DATE_RANGE = re.compile(r"\d{8}-\d{8}")
REGEX_WEEKDAY = re.compile(r"[MDFS][oira]")

class DateTimeUtil():
    """ Util Functions for Date and Time  """

    @staticmethod
    def get_datetime_from_string(datetime_s:str,local_tz='Europe/Berlin')->DateTime:
        """ returns datetime for date string with timezone
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

        if ( ( len(re.findall(reg_expr_dt, datetime_s)) == 1 ) ): # date time format
            try:
                timezone_loc = pytz.timezone(local_tz)
                dt_s = datetime_s[0:4]+"-"+datetime_s[5:7]+"-"+datetime_s[8:10]+" "+datetime_s[11:13]+"-"+datetime_s[14:16]+"-"+datetime_s[17:19]
                dt = DateTime.strptime(dt_s,"%Y-%m-%d %H-%M-%S")
                dt = timezone_loc.localize(dt) # abstain from datetime.replace :-) ...
            except:
                return 0

        elif  ( len(re.findall(reg_expr_utc2, datetime_s)) == 1 ): # utc2 format
            datetime_s = datetime_s[:-5] + "+00:00"
        elif ( len(re.findall(reg_expr_utc, datetime_s)) == 1 ): # utc format
            datetime_s = datetime_s[:-1] + "+00:00"
        elif ( len(re.findall(reg_expr_tz, datetime_s)) == 1 ): # time zone format
            pass # this time zone already has the correct format
        else:
            logger.warning(f"can't evaluate time format {datetime_s} ")
            return 0

        if dt is None:
            # omit colon
            try:
                dt_s = datetime_s[:-3]+datetime_s[-2:]
                dt = DateTime.strptime(dt_s, "%Y-%m-%dT%H:%M:%S%z")
            except:
                return None

        logger.debug(f"[DateTimeUtil] IN:{datetime_s_in}, dt:{dt}, tz:{dt.tzinfo} utc:{dt.utcoffset()}, dst:{dt.tzinfo.dst(dt)}")

        return dt

    @staticmethod
    def get_timestamp(datetime_s:str,local_tz='Europe/Berlin') -> int:
        """ returns UTC timestamp for date string  """

        dt = DateTimeUtil.get_datetime_from_string(datetime_s,local_tz)
        ts = int(dt.timestamp())
        logger.debug(f"[DateTimeUtil] Datestring: {datetime_s} Timezone {local_tz} Timestamp: {ts}")

        return ts

    @staticmethod
    def get_time_offset(time_device:str,time_gps:str)->timedelta:
        """ helps to calculate offset due to difference of GPS Logger and Device Time Difference
            difference = time(gps) - time(device) > time(gps) = time(device) + difference
            returns a timedelta object
        """
        try:
            ts_gps = DateTime.fromtimestamp(DateTimeUtil.get_timestamp(time_gps))
            ts_cam = DateTime.fromtimestamp(DateTimeUtil.get_timestamp(time_device))
        except:
            raise Exception(f"GPS Timestamp {time_gps} or Camera Timestamp {time_device} not correct")

        delta_time = ts_gps - ts_cam

        logger.debug(f"[DateTimeUtil] GPS:{time_gps} - Camera:{time_device} = Time Offset:{(delta_time//timedelta(seconds=1))}")

        return delta_time

    @staticmethod
    def get_localized_datetime(dt_in,tz_in="Europe/Berlin",tz_out="UTC",as_timestamp=False)->DateTime:
        """helper method to get non naive datetime (based on input and output timezone),
           input date can be string or datetime,
           timezone can be string or pytz object, optionally returns also as utc timestamp"""

        reg_expr_datetime = "\\d{4}[-:]\\d{2}[:-]\\d{2} \\d{2}[:-]\\d{2}[:-]\\d{2}"

        def get_tz_info(tz):
            if isinstance(tz,pytz.BaseTzInfo):
                tz_info = tz
            elif isinstance(tz_in,str):
                tz_info = pytz.timezone(tz)
            else:
                tz_info = pytz.timezone("UTC")
            return tz_info

        if dt_in is None:
            return None

        tz_utc = pytz.timezone("UTC")
        pytz_in = get_tz_info(tz_in)
        pytz_out = get_tz_info(tz_out)

        if isinstance(dt_in,DateTime):
            dt = dt_in
        elif isinstance(dt_in,str):
            # convert date hyphens
            if (len(re.findall(reg_expr_datetime, dt_in))==1):
                dt_in = (dt_in[:10].replace(":","-")+dt_in[10:])

            # utc code
            if dt_in[-1] == "Z":
                dt_in = dt_in[:-1]+"+00:00"
            dt = parse(dt_in)

        dt = None
        tz_info = dt.tzinfo

        # naive datetime, convert to input timezone
        if tz_info is None:
            dt = pytz_in.localize(dt)
            tz_info = dt.tzinfo

        # convert to utc time formats
        if (isinstance(tz_info,tzutc)) or (isinstance(tz_info,tzoffset)):
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
        logger.debug(f"[DateTimeUtil]   -> Timestamp {dt_utc.timestamp()} with UTC datetime {DateTime.utcfromtimestamp(dt_utc.timestamp())}")
        return out

    @staticmethod
    def get_easter_sunday(year:int,verbose=False)->DateTime|dict:
        """ Calculates easter sunday
            Arguments
            year: Year
            verbose: if true returns a detailed dictionary of calculations date object otherwise
            showinfo: show information
            Returns: Date or Info Dictionary of Easter Sunday
            Reference: https://www.tondering.dk/claus/cal/easter.php
        """
        G = ( year % 19 ) + 1
        epact_julian = (11*(G-1)) % 30 # epact in julian calendar
        C = ( year // 100 ) + 1 # century
        S = (3*C) // 4 # solar equation, difference Julian vs. Gregorian
        L = (8*C+5) // 25 # Lunar Equation, difference between the Julian calendar and the Metonic cycle.

        # Gregorian EPact
        # The number 8 is a constant that calibrates the starting point of the Gregorian Epact so
        # that it matches the actual age of the moon on new year’s day.
        epact_gregorian = ( epact_julian - S + L + 8 )

        # adjust so that gregorian epact is within range of 1 to 30
        if epact_gregorian == 0:
            epact_gregorian = 30
        elif ( epact_gregorian > 30 ) or ( epact_gregorian < 0):
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
            elif ( epact_gregorian == 25 ) and ( G < 11 ):
                d_offset -= 1

        d_fm = d_fm - timedelta(days=d_offset)
        d_weekday = d_fm.isoweekday()

        # offset calculate nex sunday / in case its a sunday it will be follow up sunday
        d_e_offset = 7 - ( d_weekday % 7 )
        d_easter = d_fm + timedelta(days=d_e_offset)
        logger.debug(f" {year}|G:{str(G).zfill(2)} Epact:{str(epact_gregorian).zfill(2)}|C:{C} S:{S} L:{L}"+
                     f"|F.Moon {d_fm}-{d_fm.strftime('%a')}|Eastern {d_easter}/{d_easter.strftime('%a')}|")

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
    def get_holiday_dates(year:int,show_info=False)->dict:
        """ Calculates holiday dates for Baden Württemberg for given year """

        holiday_list = {"Neujahr":{"month":1,"day":1,"holiday":1},
                        "Dreikönig":{"month":1,"day":6,"holiday":1},
                        "Rosenmontag":{"holiday":0,"offset":-48},
                        "Aschermittwoch":{"holiday":0,"offset":-46},
                        "Karfreitag":{"holiday":1,"offset":-2},
                        "Ostersonntag":{"holiday":0,"offset":0},
                        "Ostermontag":{"holiday":1,"offset":1},
                        "1.Mai":{"month":5,"day":1,"holiday":1},
                        "Himmelfahrt":{"holiday":1,"offset":39},
                        "Pfingstsonntag":{"holiday":0,"offset":49},
                        "Pfingstmontag":{"holiday":1,"offset":50},
                        "Fronleichnam":{"holiday":1,"offset":60},
                        "Dt Einheit":{"month":10,"day":3,"holiday":1},
                        "Allerheiligen":{"month":11,"day":1,"holiday":1},
                        "Heiligabend":{"month":12,"day":24,"holiday":1},
                        "1.Weihnachtstag":{"month":12,"day":25,"holiday":1},
                        "2.Weihnachtstag":{"month":12,"day":26,"holiday":1},
                        "Silvester":{"month":12,"day":31,"holiday":1}}

        d_easter = DateTimeUtil.get_easter_sunday(year)

        out_dict ={}
        num_holidays = 0

        if show_info:
            print(f"\n--- Holiday Days for year {year} ---")

        for h,v in holiday_list.items():
            # check if it is a fixed holiday
            offset = holiday_list[h].get("offset",None)
            if offset is None:
                d_holiday = DateTime(year,v["month"],v["day"])
            else:
                d_holiday = d_easter + timedelta(days=v["offset"])
            d_holiday = DateTime(d_holiday.year,d_holiday.month,d_holiday.day)

            weekday = d_holiday.isoweekday()
            v["weekday"] = weekday
            v["year"] = year
            v["d"] = DateTime(d_holiday.year,d_holiday.month,d_holiday.day)
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
    def is_leap_year(y)->bool:
        """ check whether year is leap year """
        ly = False

        if ( y % 4 == 0 ) and not ( y % 100 == 0 ):
            ly = True

        if ( y % 100 == 0 ) and not ( y % 400 == 0 ):
            ly = False

        if ( y % 400 == 0 ):
            ly = True

        return ly

    @staticmethod
    def get_1st_isoweek_date(y:int)->DateTime:
        """ returns monday date of first isoweek of a given calendar year
            https://en.wikipedia.org/wiki/ISO_week_date
            W01 is the week containing 1st Thursday of the Year
        """
        d_jan1 = date(y,1,1)
        wd_jan1 = d_jan1.isoweekday()
        # get the monday of this week
        d_monday_w01 = d_jan1 - timedelta(days=(wd_jan1-1))
        # majority of days in new calendar week
        if wd_jan1 > 4:
            d_monday_w01 += timedelta(days=7)
        dt_monday_w01=DateTime(d_monday_w01.year,d_monday_w01.month,d_monday_w01.day)

        return dt_monday_w01

    @staticmethod
    def get_isoweekyear(y:int)->dict:
        """" returns isoweek properties for given calendar year as dictionary:
            1st and last monday of isoweek year, number of working weeks
        """
        d_first = DateTimeUtil.get_1st_isoweek_date(y)
        d_last = DateTimeUtil.get_1st_isoweek_date(y+1)
        working_weeks = (d_last - d_first).days // 7
        d_last = DateTimeUtil.get_1st_isoweek_date(y+1) - timedelta(days=7)
        isoweekyear = {}
        isoweekyear["first_monday"] = d_first
        isoweekyear["last_monday"] = d_last
        isoweekyear["last_day"] = d_last + timedelta(days=6)
        isoweekyear["weeks"] = working_weeks
        isoweekyear["year"] = y

        return isoweekyear

    @staticmethod
    def isoweek(d:DateTime):
        """" returns isoweek (isoweek,calendar year,number of passed days in calendar year) for given date """
        y = d.year

        wy = DateTimeUtil.get_isoweekyear(y)

        # check if date is in boundary of current calendar year
        if ( d < wy["first_monday"] ):
            wy = DateTimeUtil.get_isoweekyear(y-1)
        elif ( d > wy["last_day"] ):
            wy = DateTimeUtil.get_isoweekyear(y+1)

        iso = {}
        iso["year"] = wy["year"]
        iso["leap_year"] = DateTimeUtil.is_leap_year(wy["year"])
        iso["weeks_year"] = wy["weeks"]
        iso["day_in_year"] = ( d - wy["first_monday"]).days + 1
        iso["calendar_week"] = ceil( iso["day_in_year"] / 7 )
        iso["weekday"] = d.isoweekday()
        return iso

    @staticmethod
    def create_calendar(year:int,daytype_list:DayTypeListType=None):
        """ create a calendar """
        return Calendar(year,daytype_list)

    @staticmethod
    def get_dates_from_range(daterange:str)->list:
        """ Transforms a string of format yyyymmdd-YYYYMMDD into a list of dates """
        out = []
        _date_from,_date_to = [DateTime.strptime(_d,"%Y%m%d") for _d in daterange.split("-")]
        _date = _date_from
        while _date <= _date_to:
            out.append(_date)
            _date = _date + timedelta(days=1)
        return out

class Calendar():
    """ Calendar Object """
    def __init__(self,year:int,daytype_list:DayTypeListType=None):
        """ Constructor """
        self._year : int  = year
        # get first monday of isoweek
        self._isoweek_info : dict  = DateTimeUtil.get_isoweekyear(year)
        self._year_info : YearModelType = None
        self._create_year_info()
        self._daytype_list = {}
        if daytype_list:
            self._daytype_list = daytype_list
        # adds daytpe info
        self._set_daytypes()
        # adds information
        self._add_info()

    @staticmethod
    def _get_day_type(week_info:dict,holiday:str,workday_home:bool=False)->DayTypeEnum:
        """ determines the daytype """
        if workday_home:
            day_type = DayTypeEnum.WORKDAY_HOME
        else:
            day_type = DayTypeEnum.WORKDAY

        if week_info["weekday"]>5:
            day_type = DayTypeEnum.WEEKEND

        if holiday is not None:
            day_type = DayTypeEnum.HOLIDAY

        return day_type

    @staticmethod
    def get_month_info(year:int,month:int)->MonthModelType:
        """ gets date information as Pydantic Model """
        # get this date for calculation of number of days
        dt_dec31 = DateTime(year,1,1) - timedelta(days=1)
        out = {}
        # get holidays
        _holidays = DateTimeUtil.get_holiday_dates(year)
        # get days in month
        _days_in_month = DAYS_IN_MONTH.get(month)
        if month == 2 and DateTimeUtil.is_leap_year(year):
            _days_in_month += 1
        for _d in range(1,_days_in_month+1):
            _dt = DateTime(year,month,_d)
            _dt_s = _dt.strftime("%Y%m%d")
            _y = _dt.year
            _m = _dt.month
            _d = _dt.day
            _weekinfo = DateTimeUtil.isoweek(_dt)
            _day_in_year = (_dt - dt_dec31).days
            _week_day_num = _weekinfo.get("weekday")
            _week_day_s = WEEKDAY[_week_day_num]
            _calendar_week = _weekinfo.get("calendar_week")
            _holiday = _holidays.get(_dt)
            if _holiday:
                _holiday = _holiday.get("name")
            # get day type
            _day_type = Calendar._get_day_type(_weekinfo,_holiday)

            _day_info = {"datetime_s":_dt_s,
                         "datetime":_dt,
                         "year":_y,
                         "month":_m,
                         "day":_d,
                         "day_in_year":_day_in_year,
                         "weekday_num":_week_day_num,
                         "weekday_s":_week_day_s,
                         "isoweeknum":_calendar_week,
                         "holiday":_holiday,
                         "day_type":_day_type}
            out[_dt_s] = CalendarDayType(**_day_info)
        return out


    @staticmethod
    def get_year_info(year:int)->YearModelType:
        """ returns a year as matrix [month][day]
            also adds vacation list (either as date YYYYMMDD or as range
                                     YYYYMMDD-yyyymmdd)
        """
        out = {}
        for _month in range(1,13):
            _month_info = Calendar.get_month_info(year,_month)
            # transform it into a dict using day ints
            _month_info = dict([(_info.day,_info) for _info in _month_info.values()])
            out[_month]=_month_info
        return out

    def _create_year_info(self)->None:
        """ create a year calendar """
        self._year_info = Calendar.get_year_info(self._year)

    def get_weekdays(self,weekdays:list=None)->list:
        """ get all weekdays ["Mo",...]from list """
        out = []
        if isinstance(weekdays,str):
            weekdays = weekdays.split(" ")
        for _month in range(1,13):
            _days_info = list(self._year_info[_month].values())
            for day_info in _days_info:
                if day_info.weekday_s in weekdays:
                    out.append(day_info.datetime)
        return out

    def _get_daytype_dates(self,daytype:DayTypeEnum,date_s:str=None)->list:
        """ get datetype_dates """
        # get all dates in one string and apply regexes from there
        if date_s:
            _date_s = date_s
        else:
            _date_s = " ".join(self._daytype_list.get(daytype,[]))
        _date_ranges =  REGEX_DATE_RANGE.findall(_date_s)
        dates = [DateTimeUtil.get_dates_from_range(_dr) for _dr in _date_ranges]
        dates = [_d for _daterange_list in dates for _d in _daterange_list]
        _dates_single = [DateTime.strptime(_d[1],"%Y%m%d") for _d in REGEX_YYYYMMDD.findall(_date_s)]
        dates.extend(_dates_single)
        _weekdays_s = REGEX_WEEKDAY.findall(_date_s)
        _week_dates = self.get_weekdays(_weekdays_s)
        dates.extend(_week_dates)
        dates = list(tuple(sorted(dates)))
        return dates

    def _add_info(self)->None:
        """ adds information  """
        _info_list = self._daytype_list.get(DayTypeEnum.INFO,[])
        for _info in _info_list:
            _day_list = self._get_daytype_dates(DayTypeEnum.INFO,_info)
            for _day in _day_list:
                if _day.year != self._year:
                    continue
                _day_info = self._year_info[_day.month][_day.day]
                _info_value = _day_info.info
                if isinstance(_info_value,list):
                    _info_value.append(_info)
                else:
                    _info_value = [_info]
                _day_info.info = _info_value

    def _set_daytype(self,daytype:DayTypeEnum)->None:
        """ setting a specific daytype """
        _days_list = self._get_daytype_dates(daytype)
        for _day in _days_list:
            _y = _day.year
            if self._year != _y:
                continue
            _d = _day.day
            _m = _day.month
            _day_info = self._year_info[_m][_d]
            # only change info if working day
            if _day_info.day_type in [DayTypeEnum.WORKDAY,DayTypeEnum.WORKDAY_HOME]:
                _day_info.day_type = daytype

    def _set_daytypes(self)->None:
        """ setting the daytypes in a specific order"""
        # some order needs to be maintained
        _all_daytypes = [DayTypeEnum.WORKDAY_HOME,DayTypeEnum.PARTTIME,
                         DayTypeEnum.FLEXTIME,DayTypeEnum.VACATION]
        _daytypes = list(self._daytype_list.keys())
        for _daytype in _all_daytypes:
            if _daytype not in _daytypes:
                continue
            self._set_daytype(_daytype)

    def _get_calendar365(self)->Dict[int,CalendarDayType]:
        """ gets the calendar as dict """
        out = {}
        for _m in range(1,13):
            _day_infos = list(self._year_info[_m].values())
            for _day_info in _day_infos:
                out[_day_info.day_in_year]=_day_info
        return out

    @property
    def stats(self)->dict:
        """ get number of days in stats """
        out = {}
        _num_total = 0
        for _month,_month_info in self._year_info.items():
            _month_out={"weekday_s":{},"day_type":{},"holiday":[]}
            for _day,_day_info in _month_info.items():
                _day_type = _day_info.day_type.value
                _num_days = _month_out["day_type"].get(_day_type,0)+1
                _month_out["day_type"][_day_type] = _num_days
                _weekday_s = _day_info.weekday_s
                _num_days = _month_out["weekday_s"].get(_weekday_s,0)+1
                _month_out["weekday_s"][_weekday_s] = _num_days
                _holiday = _day_info.holiday
                if _holiday:
                    _d = f" ({_weekday_s}, {_day_info.datetime.strftime('%d.%m')})"
                    _month_out["holiday"].append(_holiday+_d)
            out[_month]=_month_out
        return out

    @property
    def stats_sum(self)->dict:
        """ Cumulated stats per year """
        out = {"weekday_s":{},"day_type":{},"holiday":[]}
        _stats_month = self.stats
        for _,_month_info in _stats_month.items():
            _weekday_info = _month_info["weekday_s"]
            for _day,_num in _weekday_info.items():
                _num_total = out["weekday_s"].get(_day,0)
                out["weekday_s"][_day] = _num_total + _num
            _day_type_info = _month_info["day_type"]

            for _daytype,_num in _day_type_info.items():
                _num_total = out["day_type"].get(_daytype,0)
                out["day_type"][_daytype] = _num_total + _num

            out["holiday"].extend(_month_info["holiday"])
        return out

    def get_day_info(self,month:int,day:int)->CalendarDayType:
        """ returns the calendar info """
        return self._year_info[month][day]

    def get_calendar_table(self,num_months:int=6)->list:
        """ creates tabular format """
        num_tables = 12 // num_months
        out = []
        for _num_table in range(num_tables):
            _first_month = _num_table*num_months+1
            _last_month = _first_month + num_months
            _table = []
            for _day in range(1,32):
                _row = [str(_day).zfill(2)]
                for _month in range(_first_month,_last_month):
                    _info = self._year_info[_month].get(_day)
                    _value = None
                    if _info is not None:
                        _value = (_month,_day)
                    _row.append(_value)
                _table.append(_row)
            out.append(_table)

        return out

