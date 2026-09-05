"""ドメインモデル — 混雑・天気・ステータスのデータ構造。

含まれるもの:
- RecordStatus — 記録の状態（OK / maintenance / stale_data 等）
- Thresholds, PCounterPayload — JSON から取り出した生データ
- CrowdingSnapshot — 取得直後の混雑1件分
- WeatherSnapshot — 天気1件分
- CrowdingRecord — スプレッドシート1行分

処理の流れ:
1. fetch 層が JSON/HTML から Payload / Snapshot を組み立てる
2. record_format が Snapshot + Weather を CrowdingRecord に変換
3. store 層が CrowdingRecord をシートに書く
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class RecordStatus(StrEnum):
    """スプレッドシート「ステータス」列に書く値。"""

    OK = "OK"
    SKIPPED_CLOSED = "skipped_closed"
    MAINTENANCE = "maintenance"
    STALE_DATA = "stale_data"
    ERROR = "error"


@dataclass(frozen=True)
class Thresholds:
    """混雑4段階の人数閾値（サイト JSON の rank1〜4）。"""

    rank1: int
    rank2: int
    rank3: int
    rank4: int


@dataclass(frozen=True)
class PCounterPayload:
    """p-counter JSON 1セクション分のパース結果。"""

    count: int
    time_calc: str
    maintenance: bool
    thresholds: Thresholds


@dataclass(frozen=True)
class CrowdingSnapshot:
    """混雑取得直後の1件分（シート行に変換前）。"""

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
        """取得失敗時の空レコード（各列を空欄にする）。"""
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
    """スプレッドシート「混雑履歴」1 行分（16列）。"""

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
