"""Google スプレッドシートへの追記。

含まれるもの:
- SheetsWriter — 混雑履歴シートへ1行追記
- HEADER / LEGACY_HEADER — 列定義

処理の流れ:
1. サービスアカウントでスプレッドシートに接続
2. 指定シートを取得（無ければ作成してヘッダー行を書く）
3. ヘッダーがずれていれば16列に修正
4. 1行を append_row で追記 — 失敗時は例外を cli へ伝播
"""

from __future__ import annotations

from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials
from gspread.utils import ValueInputOption

from hakata_gym_crowding.domain.models import CrowdingRecord, CrowdingSnapshot
from hakata_gym_crowding.domain.record_format import (
    build_crowding_record,
    record_to_row,
)

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


def _col_letter(column_count: int) -> str:
    """列数からスプレッドシート列記号（A, B, … Z, AA）を返す。"""
    column_letters = ""
    n = column_count
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        column_letters = chr(65 + remainder) + column_letters
    return column_letters


HEADER_RANGE = f"A1:{_col_letter(len(HEADER))}1"


class SheetsWriter:
    """混雑履歴シートへ1行追記する。

    集まっているもの:
    - データ: spreadsheet_id, 認証ファイルパス, シート名
    - 処理: append_record, append_snapshot

    バリデーション: ヘッダー行の自動修正あり
    """

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
        """組み立て済みレコードを1行追記する。

        受け取る: CrowdingRecord（16列分の値）
        返す: なし（副作用: シートに1行追加）
        例外: gspread / 認証エラーはそのまま伝播
        """
        worksheet = self._get_worksheet()
        worksheet.append_row(
            record_to_row(record),
            value_input_option=ValueInputOption.user_entered,
        )

    def append_snapshot(
        self,
        snapshot: CrowdingSnapshot,
        *,
        weather_fetch_failed: bool = False,
    ) -> None:
        """スナップショットからレコードを組み立てて追記する（天気なしの簡易経路）。

        受け取る: 混雑スナップショット、天気失敗フラグ
        返す: なし
        """
        row = build_crowding_record(
            snapshot,
            None,
            weather_fetch_failed=weather_fetch_failed,
        )
        self.append_record(row)

    def _get_worksheet(self) -> gspread.Worksheet:
        """接続済み worksheet を返す（同一実行内はキャッシュ）。

        受け取る: なし
        返す: gspread Worksheet
        例外: 認証・権限エラー
        """
        # 同一実行内では worksheet を使い回す
        if self._worksheet is not None:
            return self._worksheet

        credentials = Credentials.from_service_account_file(
            str(self._credentials_path),
            scopes=SCOPES,
        )
        client = gspread.authorize(credentials)
        spreadsheet = client.open_by_key(self._spreadsheet_id)
        # シート取得
        # ・成功 → worksheet を返す
        # ・WorksheetNotFound → 新規シート作成 + ヘッダー行追加
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
        # 手動編集でヘッダーがずれた場合は正しい16列ヘッダーに戻す
        if first_row != HEADER:
            worksheet.update([HEADER], range_name=HEADER_RANGE)

        self._worksheet = worksheet
        return worksheet
