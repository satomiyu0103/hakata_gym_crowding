"""migrate_sheet_columns の行変換テスト。"""

from hakata_gym_crowding.domain.record_format import convert_legacy_row


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
