#---------------------------------------------------------------------------
# Misc utility functions
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
# Setup functions
#---------------------------------------------------------------------------
from contextlib import suppress

def getSetupInfo(reqment):
    """This function will try and return the info from setuptools"""
    retval = {}
    with suppress(ImportError):
        from pkg_resources import get_distribution
        from pkg_resources import DistributionNotFound, VersionConflict
        try:
            pkgInfo = get_distribution(reqment).get_metadata('PKG-INFO')
        except (DistributionNotFound, VersionConflict, FileNotFoundError):
            pkgInfo = ""
        from email import message_from_string
        msg = message_from_string(pkgInfo)
        for key in msg:
            values = msg.get_all(key)
            newValues = []
            for value in values:
                newValues.append("".join(value.split("\n"))[:72])
            values = newValues
            if len(values) == 1:
                retval[key] = values[0]
            else:
                retval[key] = values
    return retval

def getGitTag():
    from subprocess import check_output, CalledProcessError
    try:
        tag = check_output("git describe --tags --always", shell=True)
        tag = tag.strip().decode('utf-8')
    except CalledProcessError:
        tag = ""
    return tag

#---------------------------------------------------------------------------
# String/text functions
#---------------------------------------------------------------------------
import re
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

def secureSettings(settings):
    retval = {}
    for key, value in settings.items():
        if 'secret' in key:
            value = '$$$$$$$$$$$$$'
        elif 'password' in key:
            value = '*************'
        elif 'url' in key:
            pwdMatch = re.search(r'(.*:)([^@]+)(@.*)', value)
            if pwdMatch:
                value = "{0}**********{2}".format(*pwdMatch.groups())
        retval[key] = value
    return retval

def dollars(num):
    return "${:,.2f}".format(num) if num >= 0 else "-${:,.2f}".format(-num)

#---------------------------------------------------------------------------
# Grid conversion function
#---------------------------------------------------------------------------
import pytz
from numbers import Number
from datetime import datetime
from .dt import localDateTimeStr

def recsToRows(recs, headings, tz=pytz.utc):
    """Translate records to lists of displayable strings"""
    rows = []
    for rec in recs:
        row = []
        for field, heading in headings:
            value = getattr(rec, field, "")
            if value is None:
                value = ""
            elif isinstance(value, datetime):
                value = localDateTimeStr(value, tz)
            elif isinstance(value, Number):
                if heading.lower() == "id" or heading[-1] == "#":
                    value = str(value)
                else:
                    value = "{:,}".format(value)
            else:
                value = str(value)
            row.append(value)
        rows.append(row)
    return rows

