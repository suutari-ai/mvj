from datetime import datetime, tzinfo
from typing import Optional, NewType


AwareDateTime = NewType('AwareDateTime', datetime)


def make_aware(
        dt: datetime,
        tz: tzinfo,
        *,
        is_dst: Optional[bool] = None,
) -> AwareDateTime:
    return tz.localize(dt, is_dst)  # type: ignore


def check_is_aware(dt: datetime) -> AwareDateTime:
    if not dt.tzinfo:
        raise ValueError('Given datetime is missing timezone information')
    return AwareDateTime(dt)
