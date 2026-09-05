"""既存スプレッドシート（英語6列）を日本語16列へ移行する。

使い方:
  uv run python scripts/migrate_sheet_columns.py --dry-run
  uv run python scripts/migrate_sheet_columns.py
"""

from __future__ import annotations

import argparse
import sys

from hakata_gym_crowding.config import load_settings
from hakata_gym_crowding.domain.record_format import (
    LegacyRowParseError,
    convert_legacy_row,
)
from hakata_gym_crowding.store.sheets import (
    HEADER,
    HEADER_RANGE,
    LEGACY_HEADER,
    SheetsWriter,
)


def migrate(*, dry_run: bool) -> int:
    settings = load_settings(require_sheets=True)
    writer = SheetsWriter(
        spreadsheet_id=settings.spreadsheet_id,
        credentials_path=settings.google_credentials,
        sheet_name=settings.sheet_name,
    )
    worksheet = writer._get_worksheet()
    all_values = worksheet.get_all_values()
    if not all_values:
        print("シートが空です。ヘッダー行のみ作成します。")
        if not dry_run:
            worksheet.update([HEADER], range_name=HEADER_RANGE)
        return 0

    header = all_values[0]
    data_rows = all_values[1:]

    if header == HEADER:
        print("既に新スキーマ（16列）です。移行は不要です。")
        return 0

    if header != LEGACY_HEADER:
        print(
            "想定外のヘッダーです。手動確認してください。",
            file=sys.stderr,
        )
        print(f"  現在: {header}", file=sys.stderr)
        print(f"  期待: {LEGACY_HEADER} または {HEADER}", file=sys.stderr)
        return 1

    converted: list[list[str | int | None]] = []
    skipped_count = 0
    for sheet_row_index, row in enumerate(data_rows, start=2):
        if not any(cell.strip() for cell in row):
            continue
        try:
            converted.append(convert_legacy_row(row))
        except LegacyRowParseError as exc:
            skipped_count += 1
            print(f"  行{sheet_row_index}: スキップ — {exc}", file=sys.stderr)

    if not converted and any(any(cell.strip() for cell in row) for row in data_rows):
        print("変換可能なデータ行がありません。", file=sys.stderr)
        return 1

    new_sheet = [HEADER] + converted

    print(f"移行対象: {len(converted)} 行")
    if skipped_count:
        print(f"スキップ: {skipped_count} 行（詳細は stderr）", file=sys.stderr)
    if dry_run:
        print("dry-run: 書き込みは行いません。")
        for index, row in enumerate(converted, start=2):
            print(f"  行{index}: {row[:4]}…")
        return 0

    worksheet.clear()
    col_end = HEADER_RANGE.split(":")[1].replace("1", "")
    worksheet.update(new_sheet, range_name=f"A1:{col_end}{len(new_sheet)}")
    print(f"移行完了: {len(converted)} 行を {HEADER[0]}…{HEADER[-1]} 形式に更新しました。")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="混雑履歴シートを旧6列から新16列へ移行する。")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="変換結果を表示するだけでシートは書き換えない。",
    )
    args = parser.parse_args()
    return migrate(dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
