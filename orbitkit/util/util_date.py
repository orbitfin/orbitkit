import datetime
import json
from enum import Enum
from typing import List, Optional

import pytz


class DateTimeFormat(Enum):
    '''Orbit date format
    '''

    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
    DATE_FORMAT = "%Y-%m-%d"


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime(DateTimeFormat.DATETIME_FORMAT.value)
        elif isinstance(obj, datetime.date):
            return obj.strftime(DateTimeFormat.DATE_FORMAT.value)
        else:
            return json.JSONEncoder.default(self, obj)


def get_orbit_std_datatime():
    current_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    return datetime.datetime.now(tz=current_timezone).strftime(DateTimeFormat.DATETIME_FORMAT.value)


def get_orbit_std_datatime_utc():
    return datetime.datetime.now(tz=pytz.timezone('UTC')).strftime(DateTimeFormat.DATETIME_FORMAT.value)


def get_date_range_by_base(date_range: int,
                           base_date: Optional[datetime.datetime] = None,
                           direction: str = "backward",
                           formatter: str = "%Y-%m-%d") -> List:
    """
    Get date range by datetime.
    :param date_range:
    :param base_date:
    :param direction:
    :param formatter:
    :return: A list of date range.
    """
    if date_range <= 0:
        raise Exception("Param err")

    if base_date is None:
        base_date = datetime.datetime.now()

    timedelta = datetime.timedelta(days=date_range - 1)
    if direction == "backward":
        start_date = base_date - timedelta
        end_date = base_date
    elif direction == "forward":
        start_date = base_date
        end_date = base_date + timedelta
    else:
        raise Exception("Param err")

    return get_date_range_list_v2(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), post_formatter=formatter)


def get_date_range_list_v1(start_date, end_date) -> List:
    """
    This method will return a list in which all date range are included with the very start and ending.
    :param start_date: '2019-06-03'
    :param end_date: '2019-06-05'
    :return:
    """
    datestart = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    dateend = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    dateend += datetime.timedelta(days=1)

    day_list_with_range = []
    while datestart < dateend:
        day_list_with_range.append(datestart.strftime("%Y-%m-%d"))
        datestart += datetime.timedelta(days=1)

    return day_list_with_range


def get_date_range_list_v2(start_date, end_date, pre_formatter="%Y-%m-%d", post_formatter="%Y-%m-%d") -> List:
    """
    This method will return a list in which all date range are included with the very start and ending.
    :param post_formatter: Default is %Y-%m-%d
    :param pre_formatter: Default is %Y-%m-%d
    :param start_date: '2019-06-03'
    :param end_date: '2019-06-05'
    :return:
    """
    datestart = datetime.datetime.strptime(start_date, pre_formatter)
    dateend = datetime.datetime.strptime(end_date, pre_formatter)
    dateend += datetime.timedelta(days=1)

    day_list_with_range = []
    while datestart < dateend:
        day_list_with_range.append(datestart.strftime(post_formatter))
        datestart += datetime.timedelta(days=1)

    return day_list_with_range


def get_next_day(day: str, interval: int = 1, date_format="%Y-%m-%d") -> str:
    """
    Get the next day by given date
    :param day:
    :param interval:
    :param date_format:
    :return:
    """

    target_day = datetime.datetime.strptime(day, date_format)
    next_day = target_day + datetime.timedelta(days=interval)
    return next_day.strftime(date_format)


def get_next_workday_cn(workday: str, interval: int = 1, date_format: str = "%Y-%m-%d") -> str:
    """
    Get the next trading date by Chinese calendar
    :param workday:
    :param interval:
    :param date_format:
    :return:
    """

    try:
        from chinese_calendar import is_workday
    except ImportError:
        raise ValueError(
            "Please install below packages before using this function.\n"
            "- chinese_calendar"
        )

    # Start to judge
    next_date = datetime.datetime.strptime(
        get_next_day(day=workday, interval=interval, date_format=date_format),
        date_format
    )
    while not is_workday(next_date) or next_date.weekday() in (5, 6):
        next_date = datetime.datetime.strptime(
            get_next_day(day=next_date.strftime(date_format), interval=interval, date_format=date_format),
            date_format
        )

    return next_date.strftime(date_format)
