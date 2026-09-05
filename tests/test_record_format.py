"""record_format のテスト。"""

from datetime import datetime
from zoneinfo import ZoneInfo

from hakata_gym_crowding.domain.models import (
    CrowdingSnapshot,
    RecordStatus,
    WeatherSnapshot,
)
from hakata_gym_crowding.domain.record_format import (
    build_crowding_record,
    build_remarks,
    record_to_row,
    weekday_label,
)

JST = ZoneInfo("Asia/Tokyo")


def test_weekday_label_friday() -> None:
    moment = datetime(2026, 9, 5, 17, 0, 0, tzinfo=JST)
    assert weekday_label(moment) == "土"


def test_build_remarks_empty_when_ok() -> None:
    remarks = build_remarks(RecordStatus.OK)
    assert remarks == ""


def test_build_remarks_stale_and_weather_failure() -> None:
    remarks = build_remarks(
        RecordStatus.STALE_DATA,
        weather_fetch_failed=True,
    )
    assert "stale=" in remarks
    assert "天気=取得失敗" in remarks


def test_build_crowding_record_maps_weather_columns() -> None:
    snapshot = CrowdingSnapshot(
        recorded_at=datetime(2026, 9, 5, 17, 43, 55, tzinfo=JST),
        train_count=29,
        train_level="混雑しています",
        gym_count=39,
        source_time="17:43:04",
        status=RecordStatus.OK,
    )
    weather = WeatherSnapshot(
        weather_label="曇り",
        temp_high_c=29,
        temp_low_c=28,
        wind_speed_mps=5,
        wind_direction="東",
        precipitation_pct=20,
    )
    record = build_crowding_record(snapshot, weather)
    row = record_to_row(record)

    assert len(row) == 16
    assert row[0] == "2026-09-05"
    assert row[1] == "土"
    assert row[2] == "17:43:55"
    assert row[3] == "17:43:04"
    assert row[4] == "曇り"
    assert row[5] == 29
    assert row[6] == 28
    assert row[7] == 5
    assert row[8] == "東"
    assert row[9] == 20
    assert row[10] == "OK"
    assert row[11] == 29
    assert row[14] == ""
    assert row[15] == ""
