import datetime
from ..df.base import op
from ..df.types import Definition

current_datetime = Definition(name="current_datetime", primitive="generic")
date_time = Definition(name="date_time", primitive="generic")


@op(name="dffml.datetime", outputs=current_datetime)
def date_time():
    """
    A function to generate current date and time.

    Parameters
    ----------
    output:
        Current date and time.
    """
    current_datetime = datetime.datetime.now()
    return current_datetime


@op(name="dffml.datetimeformat", outputs=date_time)
def date_time_format():
    """
    A function to modify date and time format.

    Parameters
    ----------
    output:
        Current date and time in yyyy-mm-dd hh:mm (24h)format.
    """
    currentDateTime = date_time()
    current_date = str(currentDateTime).split(" ")[0]
    current_time = str(currentDateTime).split(" ")[1].split(".")[0].split(":")
    date_time_format = str(
        current_date + " " + current_time[0] + ":" + current_time[1]
    )
    return date_time_format
