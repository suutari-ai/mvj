import json
import zlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from io import BytesIO
from typing import Iterable, List, NamedTuple, Optional, Tuple

from .enums import LogEntryKind
from .models import JobRunLogEntry

MICROSECOND = timedelta(microseconds=1)


class EntryData(NamedTuple):
    kind: LogEntryKind
    time: datetime
    text: str


class EntryInfo(NamedTuple):
    kind: LogEntryKind
    time: datetime
    length: int


@dataclass(frozen=True)
class CompactedLog:
    message_data: bytes
    entry_infos: List[EntryInfo]

    @classmethod
    def from_log_entries(
        cls, log_entries: Iterable[JobRunLogEntry],
    ) -> "CompactedLog":
        message_stream = BytesIO()
        entry_infos: List[EntryInfo] = []
        for entry in log_entries:
            msg = entry.text.encode("utf-8", errors="surrogateescape")
            entry_infos.append(EntryInfo(entry.kind, entry.time, len(msg)))
            message_stream.write(msg)
        message_data = message_stream.getvalue()
        return cls(message_data, entry_infos)

    def iterate_entry_data(self) -> Iterable[EntryData]:
        position = 0
        for (kind, time, length) in self.entry_infos:
            end_position = position + length
            encoded_text = self.message_data[position:end_position]
            text = encoded_text.decode("utf-8", "surrogateescape")
            position = end_position
            yield EntryData(kind, time, text)

    def get_boundary_data(
        self,
        time_precision: timedelta = MICROSECOND,
    ) -> Tuple[List[int], List[int], List[int]]:
        ts0: Optional[datetime] = None
        total_delta_so_far: int = 0
        kinds: List[int] = []
        time_deltas: List[int] = []
        lengths: List[int] = []

        for (kind, ts, length) in self.entry_infos:
            if ts0 is None:
                ts0 = ts
            delta = int((ts - ts0) / time_precision) - total_delta_so_far
            total_delta_so_far += delta

            kinds.append(kind.value)
            time_deltas.append(delta)
            lengths.append(length)

        return (kinds, time_deltas, lengths)


@dataclass(frozen=True)
class CompressedLog:
    compressed_message_data: bytes
    compressed_boundaries: bytes
    first_timestamp: Optional[datetime]
    time_precision: timedelta = MICROSECOND

    @classmethod
    def from_log_entries(
        cls,
        log_entries: Iterable[JobRunLogEntry],
        level: int = -1,
        time_precision: timedelta = MICROSECOND,
    ) -> "CompressedLog":
        log = CompactedLog.from_log_entries(log_entries)
        return cls.from_compacted_log(log, level, time_precision)

    @classmethod
    def from_compacted_log(
        cls,
        log: CompactedLog,
        level: int = -1,
        time_precision: timedelta = MICROSECOND,
    ) -> "CompressedLog":
        compressed_message_data = zlib.compress(log.message_data, level)

        boundary_data = log.get_boundary_data(time_precision)
        boundaries_json = json.dumps(boundary_data, separators=(",", ":"))
        encoded_boundaries = boundaries_json.encode("ascii")
        compressed_boundaries = zlib.compress(encoded_boundaries, level)

        ts0 = log.entry_infos[0].time if log.entry_infos else None

        return cls(
            compressed_message_data,
            compressed_boundaries,
            first_timestamp=ts0,
            time_precision=time_precision,
        )

    def iterate_entry_data(self) -> Iterable[EntryData]:
        log = self.to_compacted_log()
        return log.iterate_entry_data()

    def to_compacted_log(self) -> "CompactedLog":
        if self.first_timestamp is None:
            return CompactedLog(b"", [])

        message_data = zlib.decompress(self.compressed_message_data)

        boundaries_json = zlib.decompress(self.compressed_boundaries)
        boundaries = json.loads(boundaries_json.decode("ascii"))

        entry_infos: List[EntryInfo] = []
        total_time = 0

        for (kind, delta, length) in zip(*boundaries):
            total_time += delta
            total_delta = total_time * self.time_precision
            entry_infos.append(
                EntryInfo(
                    kind=LogEntryKind(kind),
                    time=(self.first_timestamp + total_delta),
                    length=length,
                )
            )

        return CompactedLog(message_data, entry_infos)
