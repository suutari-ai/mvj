import enum
from typing import Any, Sequence, Tuple, Type, Union

from django.db import models

class Enum(enum.Enum):
    @classmethod
    def choices(cls) -> Sequence[Tuple[str, str]]: ...
    def __str__(self) -> str: ...


class IntEnum(int, Enum): ...

_StrOrEnum = Union[str, Type[Enum]]

class EnumFieldMixin:
    def __init__(self, enum: _StrOrEnum, **kwargs: Any) -> None: ...

class EnumField(EnumFieldMixin, models.CharField[Enum, Any]): ...

class EnumIntegerField(EnumFieldMixin, models.IntegerField[IntEnum, Any]): ...
