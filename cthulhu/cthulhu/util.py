

import datetime
from dateutil import tz


def now():
    """
    A tz-aware now
    """
    return datetime.datetime.utcnow().replace(tzinfo=tz.tzutc())
