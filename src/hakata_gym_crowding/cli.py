"""CLI エントリポイント。

処理の流れ:
1. 設定（.env）を読み込む
2. 開館時間・休館日を判定する（--force でスキップ可）
3. p-counter JSON から混雑データを取得する
4. トレーニング室ページから天気を取得する（失敗時は混雑のみ継続）
5. Google スプレッドシートへ 16 列で追記する（--dry-run 時は表示のみ）
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from hakata_gym_crowding.config import load_settings
from hakata_gym_crowding.domain.models import RecordStatus
from hakata_gym_crowding.domain.record_format import build_crowding_record
from hakata_gym_crowding.fetch.pcounter import PCounterFetcher
from hakata_gym_crowding.fetch.training_page import TrainingPageFetcher
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
        # .env 未設定など設定エラーは stderr に出して終了
        print(exc, file=sys.stderr)
        return 1

    tz = ZoneInfo(settings.timezone)
    now = datetime.now(tz=tz)
    guard = ScheduleGuard(timezone=settings.timezone)

    # 開館時間外・休館日なら取得せず終了する（--force のときは続行）
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
        # JSON 取得失敗はログに残して終了コード 1
        append_log(settings.log_file, f"error fetch={exc}")
        print(exc, file=sys.stderr)
        return 1

    # 天気取得失敗は混雑データの保存を止めない
    weather_fetch_failed = False
    weather = None
    try:
        with TrainingPageFetcher() as weather_fetcher:
            weather = weather_fetcher.fetch_weather()
    except RuntimeError as exc:
        weather_fetch_failed = True
        append_log(settings.log_file, f"warn weather={exc}")

    record = build_crowding_record(
        snapshot,
        weather,
        weather_fetch_failed=weather_fetch_failed,
    )

    line = (
        f"status={snapshot.status.value} "
        f"train={snapshot.train_count}({snapshot.train_level}) "
        f"gym={snapshot.gym_count} "
        f"weather={record.weather_label or '-'} "
        f"temp={record.temp_high_c}/{record.temp_low_c} "
        f"wind={record.wind_direction} {record.wind_speed_mps}m/s "
        f"rain={record.precipitation_pct}% "
        f"source_time={snapshot.source_time}"
    )
    print(line)

    if args.dry_run:
        append_log(settings.log_file, f"dry_run {line}")
        return 0

    # メンテナンス中はサイトが停止しているため Sheets へ書かない
    if snapshot.status == RecordStatus.MAINTENANCE:
        append_log(settings.log_file, f"maintenance {line}")
        return 0

    try:
        writer = SheetsWriter(
            spreadsheet_id=settings.spreadsheet_id,
            credentials_path=settings.google_credentials,
            sheet_name=settings.sheet_name,
        )
        writer.append_record(record)
    except Exception as exc:  # noqa: BLE001 - CLI 境界でログ化
        # Sheets 書き込み失敗はログに残して終了コード 1
        append_log(settings.log_file, f"error sheets={exc}")
        print(exc, file=sys.stderr)
        return 1

    append_log(settings.log_file, f"ok {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
