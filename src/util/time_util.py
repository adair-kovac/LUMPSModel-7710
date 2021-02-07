import datetime

import pytz


def make_date_time(month=7, day=1, hour=0, timezone="US/Mountain", year=2021):
    date_time = datetime.datetime(year=year, month=month, day=day, hour=hour)
    date_time = pytz.timezone(timezone).localize(date_time, is_dst=None)
    return date_time