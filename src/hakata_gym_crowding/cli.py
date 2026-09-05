"""CLI エントリポイント。"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from hakata_gym_crowding.config import load_settings
from hakata_gym_crowding.domain.models import RecordStatus
from hakata_gym_crowding.fetch.pcounter import PCounterFetcher
from hakata_gym_crowding.logging_utils import append_log
from hakata_gym_crowding.schedule.guard import ScheduleGuard
from hakata_gym_crowding.store.sheets import SheetsWriter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="博多体育館トレーニング室の混雑状況を取得しスプレッドシートへ追記する。",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Sheets へ書き込まず取得結果のみ表示する。",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="開館時間・休館判定を無視して実行する（デバッグ用）。",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        settings = load_settings(require_sheets=not args.dry_run)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    tz = ZoneInfo(settings.timezone)
    now = datetime.now(tz=tz)
    guard = ScheduleGuard(timezone=settings.timezone)

    if not args.force:
        decision = guard.evaluate(now)
        if not decision.should_run:
            message = f"skipped_closed reason={decision.reason}"
            append_log(settings.log_file, message)
            print(message)
            return 0

    try:
        with PCounterFetcher() as fetcher:
            snapshot = fetcher.fetch_snapshot(now)
    except RuntimeError as exc:
        append_log(settings.log_file, f"error fetch={exc}")
        print(exc, file=sys.stderr)
        return 1

    line = (
        f"status={snapshot.status.value} "
        f"train={snapshot.train_count}({snapshot.train_level}) "
        f"gym={snapshot.gym_count} source_time={snapshot.source_time}"
    )
    print(line)

    if args.dry_run:
        append_log(settings.log_file, f"dry_run {line}")
        return 0

    if snapshot.status == RecordStatus.MAINTENANCE:
        append_log(settings.log_file, f"maintenance {line}")
        return 0

    try:
        writer = SheetsWriter(
            spreadsheet_id=settings.spreadsheet_id,
            credentials_path=settings.google_credentials,
            sheet_name=settings.sheet_name,
        )
        writer.append_snapshot(snapshot)
    except Exception as exc:  # noqa: BLE001 - CLI 境界でログ化
        append_log(settings.log_file, f"error sheets={exc}")
        print(exc, file=sys.stderr)
        return 1

    append_log(settings.log_file, f"ok {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
