from datetime import date, datetime, time, timedelta

import pytz

epoch = datetime(1970, 1, 1, tzinfo=pytz.UTC)


def find_next_dst_change(timestamp, tz):
    last_dt = timestamp.astimezone(tz)
    dt = last_dt
    delta = timedelta(days=30)
    for i in range(1, 14):
        dt = tz.normalize(last_dt + (i * delta))
        if dt.utcoffset() != last_dt.utcoffset():
            break
    if dt.utcoffset() == last_dt.utcoffset():
        return None
    #raise ValueError('No DST change found for timezone {}'.format(tz))
    range_start = last_dt
    range_stop = dt
    while delta >= timedelta(seconds=30):
        half_delta = timedelta(seconds=((range_stop - range_start).total_seconds() / 2.0))
        middle = tz.normalize(range_start + half_delta)
        if middle.utcoffset() == range_start.utcoffset():
            range_start = middle
        else:
            range_stop = middle
        delta = half_delta

    secs = int(round((range_start - epoch).total_seconds() / 60.0))
    moment = (epoch + (timedelta(seconds=secs) * 60)).astimezone(tz)

    before = tz.normalize(moment - timedelta(minutes=1))
    after = tz.normalize(moment + timedelta(minutes=1))
    if before.utcoffset() != moment.utcoffset():
        return (before, moment)
    else:
        assert after.utcoffset() != moment.utcoffset()
        return (moment, after)


def find_next_dst_changes_crossing_date(in_utc=False):
    now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    for tzname in pytz.all_timezones:
        tz = pytz.timezone(tzname)
        result = find_next_dst_change(now, tz)
        if not result:
            continue

        (before, after) = result
        for change_num in [0, 1]:
            if change_num == 1:
                (before, after) = find_next_dst_change(after, tz)

            before_utc = before.astimezone(pytz.UTC)
            after_utc = after.astimezone(pytz.UTC)
            if (in_utc and before_utc.date() != after_utc.date()) or (
                    not in_utc and before.date() != after.date()):
                yield '{} -> {} | {} -> {} | {}'.format(
                    before, after, before_utc, after_utc, tzname)
