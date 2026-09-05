"""スプレッドシート行の組立（日付分割・曜日・備考）。純関数のみ。"""

from __future__ import annotations

from datetime import datetime

from hakata_gym_crowding.domain.models import (
    CrowdingRecord,
    CrowdingSnapshot,
    RecordStatus,
    WeatherSnapshot,
)

WEEKDAY_LABELS = ("月", "火", "水", "木", "金", "土", "日")


def weekday_label(moment: datetime) -> str:
    """日付から曜日ラベル（月〜日）を返す。"""
    return WEEKDAY_LABELS[moment.weekday()]


def build_remarks(
    status: RecordStatus,
    *,
    weather_fetch_failed: bool = False,
) -> str:
    """備考列の文字列を組み立てる（stale・天気失敗時のみ）。"""
    parts: list[str] = []
    if status == RecordStatus.STALE_DATA:
        parts.append("stale=計測から5分以上経過")
    if weather_fetch_failed:
        parts.append("天気=取得失敗")
    return "; ".join(parts)


def build_crowding_record(
    snapshot: CrowdingSnapshot,
    weather: WeatherSnapshot | None,
    *,
    weather_fetch_failed: bool = False,
) -> CrowdingRecord:
    """混雑スナップショットと天気を Sheets 1 行分のレコードにまとめる。"""
    weather_data = weather or WeatherSnapshot.empty()
    return CrowdingRecord(
        record_date=snapshot.recorded_at.strftime("%Y-%m-%d"),
        weekday_label=weekday_label(snapshot.recorded_at),
        fetch_time=snapshot.recorded_at.strftime("%H:%M:%S"),
        measure_time=snapshot.source_time,
        weather_label=weather_data.weather_label or "",
        temp_high_c=weather_data.temp_high_c,
        temp_low_c=weather_data.temp_low_c,
        wind_speed_mps=weather_data.wind_speed_mps,
        wind_direction=weather_data.wind_direction or "",
        precipitation_pct=weather_data.precipitation_pct,
        status=snapshot.status,
        train_count=snapshot.train_count,
        train_level=snapshot.train_level,
        gym_count=snapshot.gym_count,
        event_note="",
        remarks=build_remarks(
            snapshot.status,
            weather_fetch_failed=weather_fetch_failed,
        ),
    )


def record_to_row(record: CrowdingRecord) -> list[str | int | None]:
    """CrowdingRecord をスプレッドシート追記用の値リストに変換する。"""
    return [
        record.record_date,
        record.weekday_label,
        record.fetch_time,
        record.measure_time,
        record.weather_label,
        record.temp_high_c if record.temp_high_c is not None else "",
        record.temp_low_c if record.temp_low_c is not None else "",
        record.wind_speed_mps if record.wind_speed_mps is not None else "",
        record.wind_direction,
        record.precipitation_pct if record.precipitation_pct is not None else "",
        record.status.value,
        record.train_count,
        record.train_level,
        record.gym_count,
        record.event_note,
        record.remarks,
    ]


def convert_legacy_row(row: list[str]) -> list[str | int | None]:
    """旧6列（英語ヘッダー）の1行を新16列の値リストに変換する。"""
    if len(row) < 6:
        row = row + [""] * (6 - len(row))
    recorded_at_raw, train_count, train_level, gym_count, source_time, status_raw = row[:6]
    recorded_at = datetime.strptime(recorded_at_raw.strip(), "%Y-%m-%d %H:%M:%S")
    snapshot = CrowdingSnapshot(
        recorded_at=recorded_at,
        train_count=int(train_count),
        train_level=train_level,
        gym_count=int(gym_count),
        source_time=source_time,
        status=RecordStatus(status_raw.strip()),
    )
    record = build_crowding_record(snapshot, None)
    return record_to_row(record)
