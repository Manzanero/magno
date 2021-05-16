from django.utils import timezone


def to_datetime_iso(d):
    return timezone.localtime(d).isoformat(timespec='microseconds')
