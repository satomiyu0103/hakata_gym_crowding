"""CLI エントリポイント — 定期実行の司令塔。

含まれるもの:
- build_parser — コマンドライン引数の定義
- main — 取得から Sheets 追記までの一連処理

処理の流れ:
1. 設定読込（.env）— 失敗時は stderr + Slack 通知可なら送り、終了(1)
2. 開館時間・休館日判定（--force でスキップ可）— 対象外ならログして終了(0)
3. p-counter JSON から混雑データ取得 — 失敗時はログ + Slack 通知、終了(1)
4. トレーニング室ページから天気取得 — 失敗しても混雑のみ継続
5. Google スプレッドシートへ 16 列で追記（--dry-run 時は表示のみ、終了(0)）
6. メンテナンス中は Sheets へ書かず終了(0)
7. Sheets 追記 — 失敗時はログ + Slack 通知、終了(1)
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

from hakata_gym_crowding.config import load_settings
from hakata_gym_crowding.domain.models import RecordStatus
from hakata_gym_crowding.domain.record_format import build_crowding_record
from hakata_gym_crowding.fetch.pcounter import PCounterFetcher
from hakata_gym_crowding.fetch.training_page import TrainingPageFetcher
from hakata_gym_crowding.logging_utils import append_log
from hakata_gym_crowding.notify.slack import notify_error
from hakata_gym_crowding.schedule.guard import ScheduleGuard
from hakata_gym_crowding.store.sheets import SheetsWriter


def build_parser() -> argparse.ArgumentParser:
    """コマンドライン引数を定義する。

    受け取る: なし
    返す: --dry-run / --force を受け付ける ArgumentParser

    処理の流れ:
    1. 説明文付きパーサーを作成
    2. dry-run（Sheets 書かない）と force（開館判定スキップ）を追加
    """
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
    """定期実行のメイン処理。

    受け取る: コマンドライン引数（省略時は sys.argv）
    返す: 終了コード（0=正常終了 or 開館外スキップ, 1=エラー）

    処理の流れ:
    1. 設定読込（失敗→通知して 1）
    2. 開館判定（対象外→ログして 0）
    3. 混雑 JSON 取得（失敗→通知して 1）
    4. 天気取得（失敗しても混雑は続行）
    5. dry-run なら表示のみ 0
    6. メンテ中なら Sheets 書かず 0
    7. Sheets 追記（失敗→通知して 1）
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    default_tz = ZoneInfo("Asia/Tokyo")
    run_id = datetime.now(tz=default_tz).strftime("%Y%m%d-%H%M%S") + f"-{uuid4().hex[:4]}"

    # [手順1] 設定読込
    # ・成功 → 開館判定へ
    # ・ValueError → stderr に表示、Slack 通知可なら送り、終了(1)
    try:
        settings = load_settings(require_sheets=not args.dry_run)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        # 通知用に Sheets 不要の設定読込を試す（こちらも失敗なら通知しない）
        try:
            notify_settings = load_settings(require_sheets=False)
        except ValueError:
            notify_settings = None
        if notify_settings is not None:
            notify_error(notify_settings, run_id=run_id, stage="config", exc=exc)
        return 1

    tz = ZoneInfo(settings.timezone)
    now = datetime.now(tz=tz)
    guard = ScheduleGuard(timezone=settings.timezone)

    # [手順2] 開館時間外・休館日なら取得せず正常終了(0)（--force のときはスキップ）
    if not args.force:
        decision = guard.evaluate(now)
        if not decision.should_run:
            message = f"skipped_closed reason={decision.reason}"
            append_log(settings.log_file, message)
            print(message)
            return 0

    # [手順3] 混雑 JSON 取得
    # ・成功 → 天気取得へ
    # ・RuntimeError → ログ + Slack 通知、終了(1)
    try:
        with PCounterFetcher() as fetcher:
            snapshot = fetcher.fetch_snapshot(now)
    except RuntimeError as exc:
        append_log(settings.log_file, f"error fetch={exc}")
        notify_error(settings, run_id=run_id, stage="fetch", exc=exc)
        print(exc, file=sys.stderr)
        return 1

    # [手順4] 天気取得（失敗しても混雑データの保存は止めない）
    # ・成功 → weather に値が入る
    # ・RuntimeError → ログに warn のみ、weather_fetch_failed=True で続行
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

    # dry-run なら表示のみで終了(0)
    if args.dry_run:
        append_log(settings.log_file, f"dry_run {line}")
        return 0

    # [手順6] メンテナンス中はサイトが停止しているため Sheets へ書かず終了(0)
    if snapshot.status == RecordStatus.MAINTENANCE:
        append_log(settings.log_file, f"maintenance {line}")
        return 0

    # [手順7] Sheets 追記
    # ・成功 → ログに ok を書き、終了(0)
    # ・Exception → ログ + Slack 通知、終了(1)
    try:
        writer = SheetsWriter(
            spreadsheet_id=settings.spreadsheet_id,
            credentials_path=settings.google_credentials,
            sheet_name=settings.sheet_name,
        )
        writer.append_record(record)
    except Exception as exc:  # noqa: BLE001 - CLI 境界でログ化
        append_log(settings.log_file, f"error sheets={exc}")
        notify_error(settings, run_id=run_id, stage="sheets", exc=exc)
        print(exc, file=sys.stderr)
        return 1

    append_log(settings.log_file, f"ok {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
