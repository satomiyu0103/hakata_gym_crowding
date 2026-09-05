"""Google スプレッドシートへの追記。"""

from __future__ import annotations

from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

from hakata_gym_crowding.domain.models import CrowdingSnapshot

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADER = [
    "recorded_at",
    "train_count",
    "train_level",
    "gym_count",
    "source_time",
    "status",
]


class SheetsWriter:
    """混雑履歴シートへ1行追記する。"""

    def __init__(
        self,
        *,
        spreadsheet_id: str,
        credentials_path: Path,
        sheet_name: str = "混雑履歴",
    ) -> None:
        self._spreadsheet_id = spreadsheet_id
        self._credentials_path = credentials_path
        self._sheet_name = sheet_name
        self._worksheet: gspread.Worksheet | None = None

    def append_snapshot(self, snapshot: CrowdingSnapshot) -> None:
        worksheet = self._get_worksheet()
        worksheet.append_row(
            [
                snapshot.recorded_at.strftime("%Y-%m-%d %H:%M:%S"),
                snapshot.train_count,
                snapshot.train_level,
                snapshot.gym_count,
                snapshot.source_time,
                snapshot.status.value,
            ],
            value_input_option="USER_ENTERED",
        )

    def _get_worksheet(self) -> gspread.Worksheet:
        if self._worksheet is not None:
            return self._worksheet

        credentials = Credentials.from_service_account_file(
            str(self._credentials_path),
            scopes=SCOPES,
        )
        client = gspread.authorize(credentials)
        spreadsheet = client.open_by_key(self._spreadsheet_id)
        try:
            worksheet = spreadsheet.worksheet(self._sheet_name)
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=self._sheet_name,
                rows=1000,
                cols=len(HEADER),
            )
            worksheet.append_row(HEADER)

        first_row = worksheet.row_values(1)
        if first_row != HEADER:
            worksheet.update([HEADER], range_name="A1:F1")

        self._worksheet = worksheet
        return worksheet
