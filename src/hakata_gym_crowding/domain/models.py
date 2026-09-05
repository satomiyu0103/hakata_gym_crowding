"""ドメインモデル。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class RecordStatus(StrEnum):
    OK = "OK"
    SKIPPED_CLOSED = "skipped_closed"
    MAINTENANCE = "maintenance"
    STALE_DATA = "stale_data"
    ERROR = "error"


@dataclass(frozen=True)
class Thresholds:
    rank1: int
    rank2: int
    rank3: int
    rank4: int


@dataclass(frozen=True)
class PCounterPayload:
    count: int
    time_calc: str
    maintenance: bool
    thresholds: Thresholds


@dataclass(frozen=True)
class CrowdingSnapshot:
    recorded_at: datetime
    train_count: int
    train_level: str
    gym_count: int
    source_time: str
    status: RecordStatus
