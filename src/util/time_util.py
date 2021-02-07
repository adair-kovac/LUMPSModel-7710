import datetime

import pytz


def make_date_time(month, day, hour, timezone):
    naive_time = datetime.time(hour, 0)
    date = datetime.date(2021, month, day)
    naive_datetime = datetime.datetime.combine(date, naive_time)
    timezone = pytz.timezone(timezone)
    return timezone.localize(naive_datetime)