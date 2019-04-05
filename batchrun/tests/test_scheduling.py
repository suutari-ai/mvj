import pytest
from dateutil.parser import parse as parse_datetime

from ..enums import DstHandling
from ..scheduling import RecurrenceRule, get_next_events


def rr(
        time_spec: str,
        dst_a: str = 'dst_off',
        dst_n: str = 'skip',
        weekdays: str = '*',
        tz: str = 'Europe/Helsinki',
) -> RecurrenceRule:
    """
    Create recurrence rule with a short formula.

    The time_spec should be either in "Y M D h m" or "M D h m" format,
    where Y is spec for years, M for months, D for days of month, h for
    hours and m for minutes.
    """
    spec_parts = time_spec.split()
    if len(spec_parts) == 5:
        years = spec_parts[0]
        spec_parts = spec_parts[1:]
    else:
        years = '*'
    (months, days_of_month, hours, minutes) = spec_parts

    return RecurrenceRule.create(
        tz, years, months, days_of_month,
        weekdays=weekdays, hours=hours, minutes=minutes,
        dst_ambiguous_as=DstHandling(dst_a),
        dst_non_existent_as=DstHandling(dst_n))


GET_NEXT_EVENTS_CASES = {
    'At DST end, Daily+Hourly, Ambiguous as DST OFF': {
        'rule': rr('2019 10 26-28 2-4 */30', dst_a='dst_off'),
        'start': parse_datetime('2019-10-25 00:00 EET'),
        'result': [
            '2019-10-26 02:00:00+03:00',  # 25th 23:00 UTC
            '2019-10-26 02:30:00+03:00',  # 25th 23:30 UTC
            '2019-10-26 03:00:00+03:00',  # 26th 00:00 UTC
            '2019-10-26 03:30:00+03:00',  # 26th 00:30 UTC
            '2019-10-26 04:00:00+03:00',  # 26th 01:00 UTC
            '2019-10-26 04:30:00+03:00',  # 26th 01:30 UTC

            '2019-10-27 02:00:00+03:00',  # 26th 23:00 UTC
            '2019-10-27 02:30:00+03:00',  # 26th 23:30 UTC
            # 2019-10-27 03:00:00+03:00   = 27th 00:00 UTC not included
            # 2019-10-27 03:30:00+03:00   = 27th 00:30 UTC not included
            '2019-10-27 03:00:00+02:00',  # 27th 01:00 UTC *
            '2019-10-27 03:30:00+02:00',  # 27th 01:30 UTC *
            '2019-10-27 04:00:00+02:00',  # 27th 02:00 UTC
            '2019-10-27 04:30:00+02:00',  # 27th 02:30 UTC

            '2019-10-28 02:00:00+02:00',  # 28th 00:00 UTC
            '2019-10-28 02:30:00+02:00',  # 28th 00:30 UTC
            '2019-10-28 03:00:00+02:00',  # 28th 01:00 UTC
            '2019-10-28 03:30:00+02:00',  # 28th 01:30 UTC
            '2019-10-28 04:00:00+02:00',  # 28th 02:00 UTC
            '2019-10-28 04:30:00+02:00',  # 28th 02:30 UTC
        ]
    },
    'At DST end, Daily+Hourly, Ambiguous as DST ON': {
        'rule': rr('2019 10 26-28 2-4 */30', dst_a='dst_on'),
        'start': parse_datetime('2019-10-25 00:00 EET'),
        'result': [
            '2019-10-26 02:00:00+03:00',  # 25th 23:00 UTC
            '2019-10-26 02:30:00+03:00',  # 25th 23:30 UTC
            '2019-10-26 03:00:00+03:00',  # 26th 00:00 UTC
            '2019-10-26 03:30:00+03:00',  # 26th 00:30 UTC
            '2019-10-26 04:00:00+03:00',  # 26th 01:00 UTC
            '2019-10-26 04:30:00+03:00',  # 26th 01:30 UTC

            '2019-10-27 02:00:00+03:00',  # 26th 23:00 UTC
            '2019-10-27 02:30:00+03:00',  # 26th 23:30 UTC
            '2019-10-27 03:00:00+03:00',  # 27th 00:00 UTC *
            '2019-10-27 03:30:00+03:00',  # 27th 00:30 UTC *
            # 2019-10-27 03:00:00+02:00   = 27th 01:00 UTC not included
            # 2019-10-27 03:30:00+02:00   = 27th 01:30 UTC not included
            '2019-10-27 04:00:00+02:00',  # 27th 02:00 UTC
            '2019-10-27 04:30:00+02:00',  # 27th 02:30 UTC

            '2019-10-28 02:00:00+02:00',  # 28th 00:00 UTC
            '2019-10-28 02:30:00+02:00',  # 28th 00:30 UTC
            '2019-10-28 03:00:00+02:00',  # 28th 01:00 UTC
            '2019-10-28 03:30:00+02:00',  # 28th 01:30 UTC
            '2019-10-28 04:00:00+02:00',  # 28th 02:00 UTC
            '2019-10-28 04:30:00+02:00',  # 28th 02:30 UTC
        ]
    },
    'At DST end, Daily+Hourly, Ambiguous as SKIP': {
        'rule': rr('2019 10 26-28 2-4 */30', dst_a='skip'),
        'start': parse_datetime('2019-10-25 00:00 EET'),
        'result': [
            '2019-10-26 02:00:00+03:00',  # 25th 23:00 UTC
            '2019-10-26 02:30:00+03:00',  # 25th 23:30 UTC
            '2019-10-26 03:00:00+03:00',  # 26th 00:00 UTC
            '2019-10-26 03:30:00+03:00',  # 26th 00:30 UTC
            '2019-10-26 04:00:00+03:00',  # 26th 01:00 UTC
            '2019-10-26 04:30:00+03:00',  # 26th 01:30 UTC

            '2019-10-27 02:00:00+03:00',  # 26th 23:00 UTC
            '2019-10-27 02:30:00+03:00',  # 26th 23:30 UTC
            # 2019-10-27 03:00:00+03:00   = 27th 00:00 UTC not included
            # 2019-10-27 03:30:00+03:00   = 27th 00:30 UTC not included
            # 2019-10-27 03:00:00+02:00   = 27th 01:00 UTC not included
            # 2019-10-27 03:30:00+02:00   = 27th 01:30 UTC not included
            '2019-10-27 04:00:00+02:00',  # 27th 02:00 UTC
            '2019-10-27 04:30:00+02:00',  # 27th 02:30 UTC

            '2019-10-28 02:00:00+02:00',  # 28th 00:00 UTC
            '2019-10-28 02:30:00+02:00',  # 28th 00:30 UTC
            '2019-10-28 03:00:00+02:00',  # 28th 01:00 UTC
            '2019-10-28 03:30:00+02:00',  # 28th 01:30 UTC
            '2019-10-28 04:00:00+02:00',  # 28th 02:00 UTC
            '2019-10-28 04:30:00+02:00',  # 28th 02:30 UTC
        ]
    },

    'At DST end, Daily, Ambiguous as DST OFF': {
        'rule': rr('2019 10 26-28 3 30', dst_a='dst_off'),
        'start': parse_datetime('2019-10-25 00:00 EET'),
        'result': [
            '2019-10-26 03:30:00+03:00',  # 0:30 UTC
            '2019-10-27 03:30:00+02:00',  # 1:30 UTC
            '2019-10-28 03:30:00+02:00',  # 1:30 UTC
        ]
    },
    'At DST end, Daily, Ambiguous as DST ON': {
        'rule': rr('2019 10 26-28 3 30', dst_a='dst_on'),
        'start': parse_datetime('2019-10-25 00:00 EET'),
        'result': [
            '2019-10-26 03:30:00+03:00',  # 0:30 UTC
            '2019-10-27 03:30:00+03:00',  # 0:30 UTC
            '2019-10-28 03:30:00+02:00',  # 1:30 UTC
        ]
    },
    'At DST end, Daily, Ambiguous as SKIP': {
        'rule': rr('2019 10 26-28 3 30', dst_a='skip'),
        'start': parse_datetime('2019-10-25 00:00 EET'),
        'result': [
            '2019-10-26 03:30:00+03:00',  # 26th 0:30 UTC
            # 2019-10-27 03:30:00+03:00   = 27th 0:30 UTC not included
            # 2019-10-27 03:30:00+02:00   = 27th 1:30 UTC not included
            '2019-10-28 03:30:00+02:00',  # 28th 1:30 UTC
        ]
    },

    'At DST end, Hourly, Ambiguous as DST OFF': {
        'rule': rr('2019 10 27 2-4 0,30', dst_a='dst_off'),
        'start': parse_datetime('2019-10-27 00:00 EET'),
        'result': [
            '2019-10-27 02:00:00+03:00',  # 23:00 UTC
            '2019-10-27 02:30:00+03:00',  # 23:30 UTC
            # 2019-10-27 03:00:00+03:00   = 00:00 UTC not included
            # 2019-10-27 03:30:00+03:00   = 00:30 UTC not included
            '2019-10-27 03:00:00+02:00',  # 01:00 UTC *
            '2019-10-27 03:30:00+02:00',  # 01:30 UTC *
            '2019-10-27 04:00:00+02:00',  # 02:00 UTC
            '2019-10-27 04:30:00+02:00',  # 02:30 UTC
        ]
    },
    'At DST end, Hourly, Ambiguous as DST ON': {
        'rule': rr('2019 10 27 2-4 0,30', dst_a='dst_on'),
        'start': parse_datetime('2019-10-27 00:00 EET'),
        'result': [
            '2019-10-27 02:00:00+03:00',  # 23:00 UTC
            '2019-10-27 02:30:00+03:00',  # 23:30 UTC
            '2019-10-27 03:00:00+03:00',  # 00:00 UTC *
            '2019-10-27 03:30:00+03:00',  # 00:30 UTC *
            # 2019-10-27 03:00:00+02:00   = 01:00 UTC not included
            # 2019-10-27 03:30:00+02:00   = 01:30 UTC not included
            '2019-10-27 04:00:00+02:00',  # 02:00 UTC
            '2019-10-27 04:30:00+02:00',  # 02:30 UTC
        ]
    },
    'At DST end, Hourly, Ambiguous as SKIP': {
        'rule': rr('2019 10 27 2-4 0,30', dst_a='skip'),
        'start': parse_datetime('2019-10-27 00:00 EET'),
        'result': [
            '2019-10-27 02:00:00+03:00',  # 23:00 UTC
            '2019-10-27 02:30:00+03:00',  # 23:30 UTC
            '2019-10-27 04:00:00+02:00',  # 02:00 UTC  Note: two hour gap
            '2019-10-27 04:30:00+02:00',  # 02:30 UTC
        ]
    },

    'At DST start, Daily+Hourly, Non-existent as DST OFF': {
        'rule': rr('2018 03 24-26 2-4 */30', dst_n='dst_off'),
        'start': parse_datetime('2018-03-20 00:00 EET'),
        'result': [
            '2018-03-24 02:00:00+02:00',  # 00:00 UTC
            '2018-03-24 02:30:00+02:00',  # 00:30 UTC
            '2018-03-24 03:00:00+02:00',  # 01:00 UTC
            '2018-03-24 03:30:00+02:00',  # 01:30 UTC
            '2018-03-24 04:00:00+02:00',  # 02:00 UTC
            '2018-03-24 04:30:00+02:00',  # 02:30 UTC

            '2018-03-25 02:00:00+02:00',  # 00:00 UTC
            '2018-03-25 02:30:00+02:00',  # 00:30 UTC
            '2018-03-25 03:00:00+02:00',  # 01:00 UTC
            '2018-03-25 03:30:00+02:00',  # 01:30 UTC
            '2018-03-25 04:00:00+03:00',  # 01:00 UTC  Note: repetition
            '2018-03-25 04:30:00+03:00',  # 01:30 UTC  Note: repetition

            '2018-03-26 02:00:00+03:00',  # 23:00 UTC
            '2018-03-26 02:30:00+03:00',  # 23:30 UTC
            '2018-03-26 03:00:00+03:00',  # 00:00 UTC
            '2018-03-26 03:30:00+03:00',  # 00:30 UTC
            '2018-03-26 04:00:00+03:00',  # 01:00 UTC
            '2018-03-26 04:30:00+03:00',  # 01:30 UTC
        ]
    },
    'At DST start, Daily+Hourly, Non-existent as DST ON': {
        'rule': rr('2018 03 24-26 2-4 */30', dst_n='dst_on'),
        'start': parse_datetime('2018-03-20 00:00 EET'),
        'result': [
            '2018-03-24 02:00:00+02:00',  # 00:00 UTC
            '2018-03-24 02:30:00+02:00',  # 00:30 UTC
            '2018-03-24 03:00:00+02:00',  # 01:00 UTC
            '2018-03-24 03:30:00+02:00',  # 01:30 UTC
            '2018-03-24 04:00:00+02:00',  # 02:00 UTC
            '2018-03-24 04:30:00+02:00',  # 02:30 UTC

            '2018-03-25 02:00:00+02:00',  # 00:00 UTC
            '2018-03-25 02:30:00+02:00',  # 00:30 UTC
            '2018-03-25 03:00:00+03:00',  # 00:00 UTC  Note: repetition
            '2018-03-25 03:30:00+03:00',  # 00:30 UTC  Note: repetition
            '2018-03-25 04:00:00+03:00',  # 01:00 UTC
            '2018-03-25 04:30:00+03:00',  # 01:30 UTC

            '2018-03-26 02:00:00+03:00',  # 23:00 UTC
            '2018-03-26 02:30:00+03:00',  # 23:30 UTC
            '2018-03-26 03:00:00+03:00',  # 00:00 UTC
            '2018-03-26 03:30:00+03:00',  # 00:30 UTC
            '2018-03-26 04:00:00+03:00',  # 01:00 UTC
            '2018-03-26 04:30:00+03:00',  # 01:30 UTC
        ]
    },
    'At DST start, Daily+Hourly, Non-existent as SKIP': {
        'rule': rr('2018 03 24-26 2-4 */30', dst_n='skip'),
        'start': parse_datetime('2018-03-20 00:00 EET'),
        'result': [
            '2018-03-24 02:00:00+02:00',  # 00:00 UTC
            '2018-03-24 02:30:00+02:00',  # 00:30 UTC
            '2018-03-24 03:00:00+02:00',  # 01:00 UTC
            '2018-03-24 03:30:00+02:00',  # 01:30 UTC
            '2018-03-24 04:00:00+02:00',  # 02:00 UTC
            '2018-03-24 04:30:00+02:00',  # 02:30 UTC

            '2018-03-25 02:00:00+02:00',  # 00:00 UTC
            '2018-03-25 02:30:00+02:00',  # 00:30 UTC
            '2018-03-25 04:00:00+03:00',  # 01:00 UTC
            '2018-03-25 04:30:00+03:00',  # 01:30 UTC

            '2018-03-26 02:00:00+03:00',  # 23:00 UTC
            '2018-03-26 02:30:00+03:00',  # 23:30 UTC
            '2018-03-26 03:00:00+03:00',  # 00:00 UTC
            '2018-03-26 03:30:00+03:00',  # 00:30 UTC
            '2018-03-26 04:00:00+03:00',  # 01:00 UTC
            '2018-03-26 04:30:00+03:00',  # 01:30 UTC
        ]
    },


    'At DST start, Daily, Non-existent as DST OFF': {
        'rule': rr('2018 03 24-26 3 30', dst_n='dst_off'),
        'start': parse_datetime('2018-03-23 00:00 EET'),
        'result': [
            '2018-03-24 03:30:00+02:00',  # 1:30 UTC
            '2018-03-25 03:30:00+02:00',  # 1:30 UTC
            '2018-03-26 03:30:00+03:00',  # 0:30 UTC
        ]
    },
    'At DST start, Daily, Non-existent as DST ON': {
        'rule': rr('2018 03 24-26 3 30', dst_n='dst_on'),
        'start': parse_datetime('2018-03-23 00:00 EET'),
        'result': [
            '2018-03-24 03:30:00+02:00',  # 1:30 UTC
            '2018-03-25 03:30:00+03:00',  # 0:30 UTC
            '2018-03-26 03:30:00+03:00',  # 0:30 UTC
        ]
    },
    'At DST start, Daily, Non-existent as SKIP': {
        'rule': rr('2018 03 24-26 3 30', dst_n='skip'),
        'start': parse_datetime('2018-03-23 00:00 EET'),
        'result': [
            '2018-03-24 03:30:00+02:00',  # 24th 1:30 UTC
            # 2018-03-25 03:30:00+02:00   = 25th 1:30 UTC skipped
            '2018-03-26 03:30:00+03:00',  # 26th 0:30 UTC
        ]
    },

    'At DST start, Hourly, Non-existent as DST OFF': {
        'rule': rr('2019 03 31 2-5 0,30', dst_n='dst_off'),
        'start': parse_datetime('2019-03-31 00:00 EET'),
        'result': [
            '2019-03-31 02:00:00+02:00',  # 0:00 UTC
            '2019-03-31 02:30:00+02:00',  # 0:30 UTC
            '2019-03-31 03:00:00+02:00',  # 1:00 UTC
            '2019-03-31 03:30:00+02:00',  # 1:30 UTC
            '2019-03-31 04:00:00+03:00',  # 1:00 UTC  Note: repetition
            '2019-03-31 04:30:00+03:00',  # 1:30 UTC  Note: repetition
            '2019-03-31 05:00:00+03:00',  # 2:00 UTC
            '2019-03-31 05:30:00+03:00',  # 2:30 UTC
        ]
    },
    'At DST start, Hourly, Non-existent as DST ON': {
        'rule': rr('2019 03 31 2-5 0,30', dst_n='dst_on'),
        'start': parse_datetime('2019-03-31 00:00 EET'),
        'result': [
            '2019-03-31 02:00:00+02:00',  # 0:00 UTC
            '2019-03-31 02:30:00+02:00',  # 0:30 UTC
            '2019-03-31 03:00:00+03:00',  # 0:00 UTC  Note: repetition
            '2019-03-31 03:30:00+03:00',  # 0:30 UTC  Note: repetition
            '2019-03-31 04:00:00+03:00',  # 1:00 UTC
            '2019-03-31 04:30:00+03:00',  # 1:30 UTC
            '2019-03-31 05:00:00+03:00',  # 2:00 UTC
            '2019-03-31 05:30:00+03:00',  # 2:30 UTC
        ]
    },
    'At DST start, Hourly, Non-existent as SKIP': {
        'rule': rr('2019 03 31 2-5 0,30', dst_n='skip'),
        'start': parse_datetime('2019-03-31 00:00 EET'),
        'result': [
            '2019-03-31 02:00:00+02:00',  # 0:00 UTC
            '2019-03-31 02:30:00+02:00',  # 0:30 UTC
            '2019-03-31 04:00:00+03:00',  # 1:00 UTC
            '2019-03-31 04:30:00+03:00',  # 1:30 UTC
            '2019-03-31 05:00:00+03:00',  # 2:00 UTC
            '2019-03-31 05:30:00+03:00',  # 2:30 UTC
        ]
    },
}


@pytest.mark.parametrize('case', GET_NEXT_EVENTS_CASES.keys())
def test_get_next_events(case):
    data = GET_NEXT_EVENTS_CASES[case]

    result = list(get_next_events(data['rule'], data['start']))

    assert [str(x) for x in result] == data['result']
