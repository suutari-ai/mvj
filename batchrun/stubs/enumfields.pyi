import enum
from typing import Sequence, Tuple


class Enum(enum.Enum):
    @classmethod
    def choices(cls) -> Sequence[Tuple[str, str]]: ...

    def __str__(self) -> str: ...
