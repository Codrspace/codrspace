from datetime import datetime
from timezones.utils import adjust_datetime_to_timezone
from django.conf import settings


def localize_date(date, from_tz=None, to_tz=None):
    """
    Convert from one timezone to another
    """
    # set the defaults
    if from_tz is None:
        from_tz = settings.TIME_ZONE

    if to_tz is None:
        to_tz = "US/Central"

    date = adjust_datetime_to_timezone(date, from_tz=from_tz, to_tz=to_tz)
    date = date.replace(tzinfo=None)
    return date
