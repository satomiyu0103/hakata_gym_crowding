"""Google スプレッドシートへの追記。"""

from __future__ import annotations

from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

from hakata_gym_crowding.domain.models import CrowdingRecord, CrowdingSnapshot
from hakata_gym_crowding.domain.record_format import build_crowding_record, record_to_row

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# 旧スキーマ（移行スクリプト用）
LEGACY_HEADER = [
    "recorded_at",
    "train_count",
    "train_level",
    "gym_count",
    "source_time",
    "status",
]

HEADER = [
    "日付",
    "曜日",
    "取得時間",
    "計測時間",
    "天気",
    "最高気温",
    "最低気温",
    "風速",
    "風向",
    "降水確率",
    "ステータス",
    "トレーニングルーム利用者数",
    "混雑レベル",
    "体育館利用者数",
    "イベント",
    "備考",
]


def _col_letter(count: int) -> str:
    """列数からスプレッドシート列記号（A, B, … Z, AA）を返す。"""
    result = ""
    n = count
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result


HEADER_RANGE = f"A1:{_col_letter(len(HEADER))}1"


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

    def append_record(self, record: CrowdingRecord) -> None:
        """組み立て済みレコードを1行追記する。"""
        worksheet = self._get_worksheet()
        worksheet.append_row(
            record_to_row(record),
            value_input_option="USER_ENTERED",
        )

    def append_snapshot(
        self,
        snapshot: CrowdingSnapshot,
        *,
        weather_fetch_failed: bool = False,
    ) -> None:
        """スナップショットからレコードを組み立てて追記する（天気なしの簡易経路）。"""
        row = build_crowding_record(
            snapshot,
            None,
            weather_fetch_failed=weather_fetch_failed,
        )
        self.append_record(row)

    def _get_worksheet(self) -> gspread.Worksheet:
        # 同一実行内では worksheet を使い回す
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
            # 初回はシートとヘッダー行を自動作成
            worksheet = spreadsheet.add_worksheet(
                title=self._sheet_name,
                rows=1000,
                cols=len(HEADER),
            )
            worksheet.append_row(HEADER)

        first_row = worksheet.row_values(1)
        # 手動編集でヘッダーがずれた場合は正しい16列ヘッダーに戻す
        if first_row != HEADER:
            worksheet.update([HEADER], range_name=HEADER_RANGE)

        self._worksheet = worksheet
        return worksheet
