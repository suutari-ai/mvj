import codecs
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from io import BytesIO, StringIO
from typing import TYPE_CHECKING, Iterable, List, NamedTuple, Optional, Tuple

from dateutil.parser import parse as parse_datetime
from typing_extensions import Protocol

from .enums import LogEntryKind

if TYPE_CHECKING:
    from .models import JobRunLogEntry  # noqa: F401


MICROSECOND = timedelta(microseconds=1)


class LogEntry(Protocol):
    time: datetime
    kind: LogEntryKind
    text: str


class LogEntryDatum(NamedTuple):
    time: datetime
    kind: LogEntryKind
    text: str


class LogEntryMetadata(NamedTuple):
    time: datetime
    kind: LogEntryKind
    length: int


class LogEntryMetadataContainer(List[LogEntryMetadata]):
    @classmethod
    def deserialize(cls, serialized: str) -> "LogEntryMetadataContainer":
        data = json.loads(serialized)

        version = data.get("v")
        if version != 1:
            raise ValueError(f"Unsupported version: {version!r}")

        precision_us = data.get("p")
        if not isinstance(precision_us, int):
            raise ValueError(f"Invalid precision: {precision_us!r}")

        start = data.get("s")
        if not isinstance(start, str):
            raise ValueError(f"Invalid start timestamp: {start!r}")

        entry_data = data.get("d")
        if not isinstance(entry_data, list):
            raise ValueError(f"Invalid data type: {type(entry_data).__name__}")
        if len(entry_data) != 3:
            raise ValueError(f"Data length mismatch: {len(entry_data)}")

        first_timestamp = parse_datetime(start) if start else None
        time_precision = precision_us * MICROSECOND

        if first_timestamp is None:
            assert entry_data == [[], [], []]
            return cls()

        result = cls()
        total_time = 0
        for (delta, kind_value, length) in zip(*entry_data):
            total_time += delta
            total_delta = total_time * time_precision
            time = first_timestamp + total_delta
            kind = LogEntryKind(kind_value)
            result.append(LogEntryMetadata(time, kind, length))

        return result
    
    def serialize(self, time_precision: timedelta = MICROSECOND) -> str:
        entry_data = self.get_entry_data(time_precision)
        start = self.first_timestamp
        data = {
            "v": 1,
            "p": int(time_precision / MICROSECOND),
            "s": start.isoformat() if start else "",
            "d": entry_data,
        }
        return json.dumps(data, separators=(",", ":"), check_circular=False)

    @property
    def first_timestamp(self) -> Optional[datetime]:
        return self[0].time if self else None

    @property
    def last_timestamp(self) -> Optional[datetime]:
        return self[-1].time if self else None

    @property
    def entry_count(self) -> int:
        return len(self)

    @property
    def error_count(self) -> int:
        return sum(1 for x in self if x.kind == LogEntryKind.STDERR)

    def get_entry_data(
        self,
        time_precision: timedelta = MICROSECOND,
    ) -> Tuple[List[int], List[int], List[int]]:
        ts0: Optional[datetime] = None
        total_delta_so_far: int = 0

        time_deltas: List[int] = []
        kinds: List[int] = []
        lengths: List[int] = []

        for (ts, kind, length) in self:
            if ts0 is None:
                ts0 = ts
            delta = int((ts - ts0) / time_precision) - total_delta_so_far
            total_delta_so_far += delta

            time_deltas.append(delta)
            kinds.append(kind.value)
            lengths.append(length)

        return (time_deltas, kinds, lengths)


@dataclass(frozen=True)
class CombinedLog:
    content: str
    entry_data: str
    first_timestamp: Optional[datetime]
    last_timestamp: Optional[datetime]
    entry_count: int
    error_count: int

    @classmethod
    def from_log_entries(cls, entries: Iterable[LogEntry]) -> "CombinedLog":
        message_stream = StringIO()
        metadata_container = LogEntryMetadataContainer()
        for entry in entries:
            text = entry.text
            message_stream.write(text)
            metadata = LogEntryMetadata(entry.time, entry.kind, len(text))
            metadata_container.append(metadata)

        return cls(
            content=message_stream.getvalue(),
            entry_data=metadata_container.serialize(),
            first_timestamp=metadata_container.first_timestamp,
            last_timestamp=metadata_container.last_timestamp,
            entry_count=metadata_container.entry_count,
            error_count=metadata_container.error_count,
        )

    def iterate_entries(self) -> Iterable[LogEntryDatum]:
        metadata = self.get_metadata()
        position = 0
        for (time, kind, length) in metadata:
            text = self.content[position:(position + length)]
            position += length
            yield LogEntryDatum(time, kind, text)

    def get_metadata(self) -> LogEntryMetadataContainer:
        return LogEntryMetadataContainer.deserialize(self.entry_data)

    
# log entries
#  |
#  |  CompactedLog.from_log_entries
#  V
# CompactedLog  ( = bytes + list[LogEntryMetadata])
#  |
#  |  SerializedLog.from_compacted_log
#  V
# SerializedLog  ( = str + str)


@dataclass(frozen=True)
class CompactedLog:
    message_data: bytes
    entry_infos: List[LogEntryMetadata]

    @classmethod
    def from_log_entries(
        cls, log_entries: Iterable["JobRunLogEntry"],
    ) -> "CompactedLog":
        message_stream = BytesIO()
        entry_infos: List[LogEntryMetadata] = []
        for entry in log_entries:
            msg = entry.text.encode("utf-8", errors="surrogateescape")
            metadata = LogEntryMetadata(entry.time, entry.kind, len(msg))
            message_stream.write(msg)
            entry_infos.append(metadata)
        message_data = message_stream.getvalue()
        return cls(message_data, entry_infos)

    def iterate_entry_data(self) -> Iterable[LogEntryDatum]:
        position = 0
        for (time, kind, length) in self.entry_infos:
            end_position = position + length
            encoded_text = self.message_data[position:end_position]
            text = encoded_text.decode("utf-8", "surrogateescape")
            position = end_position
            yield LogEntryDatum(time, kind, text)

    def get_entry_data(
        self,
        time_precision: timedelta = MICROSECOND,
    ) -> Tuple[List[int], List[int], List[int]]:
        ts0: Optional[datetime] = None
        total_delta_so_far: int = 0
        kinds: List[int] = []
        time_deltas: List[int] = []
        lengths: List[int] = []

        for (ts, kind, length) in self.entry_infos:
            if ts0 is None:
                ts0 = ts
            delta = int((ts - ts0) / time_precision) - total_delta_so_far
            total_delta_so_far += delta

            kinds.append(kind.value)
            time_deltas.append(delta)
            lengths.append(length)

        return (kinds, time_deltas, lengths)


@dataclass(frozen=True)
class SerializedLog:
    content: str
    entry_data: str
    first_timestamp: Optional[datetime]
    time_precision: timedelta = MICROSECOND

    @classmethod
    def from_log_entries(
        cls,
        log_entries: Iterable["JobRunLogEntry"],
        time_precision: timedelta = MICROSECOND,
    ) -> "SerializedLog":
        log = CompactedLog.from_log_entries(log_entries)
        return cls.from_compacted_log(log, time_precision)

    @classmethod
    def from_compacted_log(
        cls,
        log: CompactedLog,
        time_precision: timedelta = MICROSECOND,
    ) -> "SerializedLog":
        content = log.message_data.decode("utf-8", "surrogateescape")

        entry_data = log.get_entry_data(time_precision)
        entry_data_json = json.dumps(entry_data, separators=(",", ":"))

        ts0 = log.entry_infos[0].time if log.entry_infos else None

        return cls(
            content=content,
            entry_data=entry_data_json,
            first_timestamp=ts0,
            time_precision=time_precision,
        )

    def iterate_entry_data(self) -> Iterable[LogEntryDatum]:
        log = self.to_compacted_log()
        return log.iterate_entry_data()

    def to_compacted_log(self) -> "CompactedLog":
        if self.first_timestamp is None:
            return CompactedLog(b"", [])

        message_data = self.content.encode("utf-8", "surrogateescape")

        entry_data = json.loads(self.entry_data)
        entry_infos: List[LogEntryMetadata] = []
        total_time = 0
        for (kind_value, delta, length) in zip(*entry_data):
            total_time += delta
            total_delta = total_time * self.time_precision
            time = (self.first_timestamp + total_delta)
            kind = LogEntryKind(kind_value)
            entry_infos.append(LogEntryMetadata(time, kind, length))

        return CompactedLog(message_data, entry_infos)
