from datetime import datetime


def now():
    return datetime.now()


def formatting(current_datetime):
    return current_datetime.strftime("%Y-%m-%d %H:%M")
