import datetime
from ..df.base import op


def date_time():
    """
    A function to generate current date and time.

    Parameters
    ----------
    output:
        Current date and time.
    """
    return datetime.datetime.now()


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
    return str(current_date + " " + current_time[0] + ":" + current_time[1])
