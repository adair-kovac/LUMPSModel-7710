import datetime
import pytz


def make_date_time(month=7, day=1, hour=0, timezone="US/Mountain", year=2021, second=0, minute=0):
    date_time = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
    date_time = localize_date_time(date_time, timezone)
    return date_time


def localize_date_time(date_time, timezone):
    return pytz.timezone(timezone).localize(date_time, is_dst=None)
