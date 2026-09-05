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
LEGACY_RECORDED_AT_FORMAT = "%Y-%m-%d %H:%M:%S"


class LegacyRowParseError(ValueError):
    """旧6列行の変換に失敗したときの例外（移行スクリプトで行単位に捕捉する）。"""


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
    # stale のときだけ理由を備考に載せる
    if status == RecordStatus.STALE_DATA:
        parts.append("stale=計測から5分以上経過")
    # 天気 HTML 取得に失敗したときも備考に残す
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
    # 天気未取得時は空の WeatherSnapshot で空欄列を埋める
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


def _parse_legacy_snapshot(row: list[str]) -> CrowdingSnapshot:
    """旧6列の文字列リストを CrowdingSnapshot に変換する。不正時は LegacyRowParseError。"""
    # 列数不足の行は空文字で6列に揃えてから読む
    if len(row) < 6:
        row = row + [""] * (6 - len(row))
    recorded_at_raw, train_count, train_level, gym_count, source_time, status_raw = row[:6]

    recorded_at_text = recorded_at_raw.strip()
    if not recorded_at_text:
        raise LegacyRowParseError("recorded_at が空です")
    # 日時は旧スキーマの固定形式のみ受け付ける
    try:
        recorded_at = datetime.strptime(recorded_at_text, LEGACY_RECORDED_AT_FORMAT)
    except ValueError:
        raise LegacyRowParseError(
            "recorded_at の形式が不正です"
            f"（期待: {LEGACY_RECORDED_AT_FORMAT}）: {recorded_at_text!r}",
        ) from None

    train_count_text = str(train_count).strip()
    if not train_count_text:
        raise LegacyRowParseError("train_count が空です")
    try:
        train_count_int = int(train_count_text)
    except ValueError:
        raise LegacyRowParseError(
            f"train_count が整数ではありません: {train_count_text!r}",
        ) from None

    gym_count_text = str(gym_count).strip()
    if not gym_count_text:
        raise LegacyRowParseError("gym_count が空です")
    try:
        gym_count_int = int(gym_count_text)
    except ValueError:
        raise LegacyRowParseError(
            f"gym_count が整数ではありません: {gym_count_text!r}",
        ) from None

    status_text = status_raw.strip()
    if not status_text:
        raise LegacyRowParseError("status が空です")
    # RecordStatus に無い文字列は行単位でスキップさせる
    try:
        status = RecordStatus(status_text)
    except ValueError:
        valid = ", ".join(member.value for member in RecordStatus)
        raise LegacyRowParseError(
            f"status が未定義です: {status_text!r}（有効: {valid}）",
        ) from None

    return CrowdingSnapshot(
        recorded_at=recorded_at,
        train_count=train_count_int,
        train_level=train_level,
        gym_count=gym_count_int,
        source_time=source_time,
        status=status,
    )


def convert_legacy_row(row: list[str]) -> list[str | int | None]:
    """旧6列（英語ヘッダー）の1行を新16列の値リストに変換する。"""
    snapshot = _parse_legacy_snapshot(row)
    record = build_crowding_record(snapshot, None)
    return record_to_row(record)
