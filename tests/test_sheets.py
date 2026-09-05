"""SheetsWriter のテスト。"""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

from hakata_gym_crowding.domain.models import CrowdingSnapshot, RecordStatus
from hakata_gym_crowding.domain.record_format import build_crowding_record
from hakata_gym_crowding.store.sheets import HEADER, HEADER_RANGE, SheetsWriter


@patch("hakata_gym_crowding.store.sheets.gspread")
def test_get_worksheet_updates_header_with_correct_argument_order(
    mock_gspread: MagicMock,
) -> None:
    worksheet = MagicMock()
    worksheet.row_values.return_value = ["wrong", "header"]

    spreadsheet = MagicMock()
    spreadsheet.worksheet.return_value = worksheet

    client = MagicMock()
    client.open_by_key.return_value = spreadsheet
    mock_gspread.authorize.return_value = client

    writer = SheetsWriter(
        spreadsheet_id="sheet-id",
        credentials_path=Path("credentials.json"),
        sheet_name="混雑履歴",
    )

    with patch(
        "hakata_gym_crowding.store.sheets.Credentials.from_service_account_file",
        return_value=MagicMock(),
    ):
        writer._get_worksheet()

    worksheet.update.assert_called_once_with([HEADER], range_name=HEADER_RANGE)


@patch("hakata_gym_crowding.store.sheets.gspread")
def test_append_record_writes_sixteen_columns(mock_gspread: MagicMock) -> None:
    worksheet = MagicMock()
    worksheet.row_values.return_value = HEADER

    spreadsheet = MagicMock()
    spreadsheet.worksheet.return_value = worksheet

    client = MagicMock()
    client.open_by_key.return_value = spreadsheet
    mock_gspread.authorize.return_value = client

    writer = SheetsWriter(
        spreadsheet_id="sheet-id",
        credentials_path=Path("credentials.json"),
        sheet_name="混雑履歴",
    )

    snapshot = CrowdingSnapshot(
        recorded_at=datetime(2026, 9, 5, 17, 43, 55, tzinfo=ZoneInfo("Asia/Tokyo")),
        train_count=29,
        train_level="混雑しています",
        gym_count=39,
        source_time="17:43:04",
        status=RecordStatus.OK,
    )
    record = build_crowding_record(snapshot, None)

    with patch(
        "hakata_gym_crowding.store.sheets.Credentials.from_service_account_file",
        return_value=MagicMock(),
    ):
        writer.append_record(record)

    worksheet.append_row.assert_called_once()
    row_values = worksheet.append_row.call_args[0][0]
    assert len(row_values) == 16
    assert row_values[2] == "17:43:55"
    assert row_values[3] == "17:43:04"

