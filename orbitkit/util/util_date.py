# -*- coding: utf-8 -*-
import datetime


def get_date_range_list_v1(start_date, end_date):
    """
    This method will return a list in which all date range are included with the very start and ending.
    :param start_date: '2019-06-03'
    :param end_date: '2019-06-05'
    :return:
    """
    datestart = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    dateend = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    dateend += datetime.timedelta(days=1)

    day_list_with_range = []
    while datestart < dateend:
        day_list_with_range.append(datestart.strftime('%Y-%m-%d'))
        datestart += datetime.timedelta(days=1)

    return day_list_with_range


def get_date_range_list_v2(start_date, end_date, pre_formatter='%Y-%m-%d', post_formatter='%Y-%m-%d'):
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
