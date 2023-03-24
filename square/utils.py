from datetime import date, datetime

from django.utils.timezone import make_aware
from pytz import timezone


def square_datetime(obj):
    if not obj:
        return
    return make_aware(
        datetime.fromtimestamp(int(obj["instantUsec"]) / 1000000),
        timezone=timezone(obj["tzName"][0]),
    )


def square_date(obj):
    return date(year=obj["year"], month=obj["monthOfYear"], day=obj["dayOfMonth"])
