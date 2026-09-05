"""migrate_sheet_columns の行変換テスト。"""

import pytest

from hakata_gym_crowding.domain.record_format import (
    LegacyRowParseError,
    convert_legacy_row,
)


def test_convert_legacy_row_maps_to_sixteen_columns() -> None:
    legacy = [
        "2026-09-05 17:43:55",
        "29",
        "混雑しています",
        "39",
        "17:43:04",
        "OK",
    ]
    row = convert_legacy_row(legacy)

    assert len(row) == 16
    assert row[0] == "2026-09-05"
    assert row[1] == "土"
    assert row[2] == "17:43:55"
    assert row[3] == "17:43:04"
    assert row[10] == "OK"
    assert row[14] == ""
    assert row[15] == ""


def test_convert_legacy_row_rejects_incomplete_row() -> None:
    with pytest.raises(LegacyRowParseError, match="recorded_at が空"):
        convert_legacy_row(["", "29", "混雑しています"])


def test_convert_legacy_row_rejects_bad_datetime() -> None:
    legacy = [
        "2026/09/05 17:43:55",
        "29",
        "混雑しています",
        "39",
        "17:43:04",
        "OK",
    ]
    with pytest.raises(LegacyRowParseError, match="recorded_at の形式が不正"):
        convert_legacy_row(legacy)


def test_convert_legacy_row_rejects_non_integer_counts() -> None:
    legacy = [
        "2026-09-05 17:43:55",
        "29.5",
        "混雑しています",
        "39",
        "17:43:04",
        "OK",
    ]
    with pytest.raises(LegacyRowParseError, match="train_count が整数ではありません"):
        convert_legacy_row(legacy)


def test_convert_legacy_row_rejects_unknown_status() -> None:
    legacy = [
        "2026-09-05 17:43:55",
        "29",
        "混雑しています",
        "39",
        "17:43:04",
        "Error",
    ]
    with pytest.raises(LegacyRowParseError, match="status が未定義"):
        convert_legacy_row(legacy)
