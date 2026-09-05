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


@dataclass(frozen=True)
class WeatherSnapshot:
    """トレーニング室ページから取得した当日天気。"""

    weather_label: str | None
    temp_high_c: int | None
    temp_low_c: int | None
    wind_speed_mps: int | None
    wind_direction: str | None
    precipitation_pct: int | None

    @classmethod
    def empty(cls) -> WeatherSnapshot:
        """取得失敗時の空レコード。"""
        return cls(
            weather_label=None,
            temp_high_c=None,
            temp_low_c=None,
            wind_speed_mps=None,
            wind_direction=None,
            precipitation_pct=None,
        )


@dataclass(frozen=True)
class CrowdingRecord:
    """スプレッドシート「混雑履歴」1 行分。"""

    record_date: str
    weekday_label: str
    fetch_time: str
    measure_time: str
    weather_label: str
    temp_high_c: int | None
    temp_low_c: int | None
    wind_speed_mps: int | None
    wind_direction: str
    precipitation_pct: int | None
    status: RecordStatus
    train_count: int
    train_level: str
    gym_count: int
    event_note: str
    remarks: str
