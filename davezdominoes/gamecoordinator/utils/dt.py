#---------------------------------------------------------------------------
# Date/Time functions
#---------------------------------------------------------------------------
from calendar import monthrange
from datetime import timedelta, datetime
import pytz

# These functions return datetimes in the timezone given
def localNow(tz):
    """Time now in the given timezone"""
    return tz.fromutc(datetime.utcnow())

def localToday(tz):
    """Date today in the given timezone"""
    return tz.fromutc(datetime.utcnow()).date()

def localDateTimeStr(naivedt, tz):
    """Formated string for the given datetime in the given timezone"""
    assert(naivedt.tzinfo is None)
    return tz.fromutc(naivedt).strftime("%Y-%m-%d %H:%M")

def localDateStr(naivedt, tz):
    """Formated string for the given date in the given timezone"""
    assert(naivedt.tzinfo is None)
    return tz.fromutc(naivedt).strftime("%Y-%m-%d")
    
