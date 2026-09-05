"""SheetsWriter のテスト。"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from hakata_gym_crowding.store.sheets import HEADER, SheetsWriter


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

    worksheet.update.assert_called_once_with([HEADER], range_name="A1:F1")
