from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Iterable, Union

import pytz

from .enums import DstHandling
from .intset import IntegerSetSpecifier


@dataclass
class RecurrenceRule:
    timezone: str

    years: IntegerSetSpecifier
    months: IntegerSetSpecifier
    days_of_month: IntegerSetSpecifier
    weekdays: IntegerSetSpecifier
    hours: IntegerSetSpecifier
    minutes: IntegerSetSpecifier

    dst_ambiguous_as: DstHandling
    dst_non_existent_as: DstHandling

    @classmethod
    def create(
            cls,
            timezone: str,
            years: str = '*',
            months: str = '*',
            days_of_month: str = '*',
            *,
            weekdays: str = '*',
            hours: str = '*',
            minutes: str = '*',
            dst_ambiguous_as: DstHandling = DstHandling.DST_OFF,
            dst_non_existent_as: DstHandling = DstHandling.SKIP,
    ) -> 'RecurrenceRule':
        return cls(
            timezone=timezone,
            years=IntegerSetSpecifier(years, 1970, 2200),
            months=IntegerSetSpecifier(months, 1, 12),
            days_of_month=IntegerSetSpecifier(days_of_month, 1, 31),
            weekdays=IntegerSetSpecifier(weekdays, 0, 6),
            hours=IntegerSetSpecifier(hours, 0, 23),
            minutes=IntegerSetSpecifier(minutes, 0, 59),
            dst_ambiguous_as=dst_ambiguous_as,
            dst_non_existent_as=dst_non_existent_as,
        )


def get_next_events(
        rule: RecurrenceRule,
        start_time: datetime,
) -> Iterable[datetime]:
    if not start_time.tzinfo:
        raise ValueError('start_time must have a timezone')

    tz = pytz.timezone(rule.timezone)
    localized_start_time = start_time.astimezone(tz)

    for d in _iter_dates_from(rule, localized_start_time.date()):
        for t in _iter_times(rule):
            naive_dt = datetime.combine(d, t)
            try:
                dt = tz.localize(naive_dt, is_dst=None)  # type: ignore
            except pytz.AmbiguousTimeError:
                if rule.dst_ambiguous_as == DstHandling.SKIP:
                    continue
                dt = tz.localize(naive_dt, is_dst=(
                    rule.dst_ambiguous_as == DstHandling.DST_ON))
            except pytz.NonExistentTimeError:
                if rule.dst_non_existent_as == DstHandling.SKIP:
                    continue
                dt = tz.localize(naive_dt, is_dst=(
                    rule.dst_non_existent_as == DstHandling.DST_ON))
            if dt >= start_time:
                yield dt


def _iter_dates_from(rule: RecurrenceRule, start_date: date) -> Iterable[date]:
    for year in rule.years:
        if year < start_date.year:
            continue

        for month in rule.months:
            if (year, month) < (start_date.year, start_date.month):
                continue

            for day in rule.days_of_month:
                try:
                    d = date(year, month, day)
                except ValueError:  # day out of range for month
                    continue  # Skip non-existing dates

                if d < start_date:
                    continue

                if _get_weekday(d) not in rule.weekdays:
                    continue

                yield d


def _iter_times(rule: RecurrenceRule) -> Iterable[time]:
    for hour in rule.hours:
        for minute in rule.minutes:
            yield time(hour, minute)


def _get_weekday(date_or_datetime: Union[date, datetime]) -> int:
    python_weekday = date_or_datetime.weekday()  # Monday = 0, Sunday = 6
    return (python_weekday + 1) % 7  # Monday = 1, Sunday = 0
