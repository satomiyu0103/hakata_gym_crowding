"""Slack Incoming Webhook による ERROR 通知。

含まれるもの:
- notify_error — 失敗時に Slack へメッセージ送信
- STAGE_META — 段階ごとの説明文

処理の流れ:
1. 通知が有効か確認（無効なら何もしない）
2. 同一エラーの重複通知を15分間抑制
3. メッセージ組立 → Webhook POST — 失敗しても本処理には例外を出さない
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import httpx

from hakata_gym_crowding.logging_utils import append_log

if TYPE_CHECKING:
    from hakata_gym_crowding.config import Settings

STAGE_META: dict[str, tuple[str, str, str]] = {
    "config": (
        "設定",
        "`.env` または認証設定が不正",
        "config/.env.example と Sheets セットアップ doc を確認",
    ),
    "fetch": (
        "混雑取得",
        "p-counter JSON の取得に失敗",
        "ネットワーク・公式サイト稼働を確認後 `--dry-run --force` で再試行",
    ),
    "sheets": (
        "Sheets 書込",
        "スプレッドシートへの追記に失敗",
        "サービスアカウント権限・SPREADSHEET_ID・API 有効化を確認",
    ),
}

DEDUP_MINUTES = 15
MAX_DETAIL_LEN = 500
POST_TIMEOUT_SECONDS = 10.0

_SLACK_WEBHOOK_RE = re.compile(r"https://hooks\.slack\.com/\S+")
_LONG_ID_RE = re.compile(r"\b[A-Za-z0-9_-]{20,}\b")
_PATH_RE = re.compile(r"(?:[A-Za-z]:\\|/)[^\s]+")


def notify_error(
    settings: Settings,
    *,
    run_id: str,
    stage: str,
    exc: BaseException,
) -> None:
    """ERROR 通知を Slack へ送る。失敗しても例外は出さない。

    受け取る: 設定、run_id、段階名（config/fetch/sheets）、例外
    返す: なし（副作用: Slack 送信 or ログのみ）
    """
    # 通知無効 or Webhook 未設定なら何もしない
    if not settings.slack_notify_enabled or not settings.slack_webhook_url:
        return

    stage_label, summary, next_action = STAGE_META[stage]
    detail = _sanitize(str(exc))
    # 15分以内の同一エラーは再送しない
    if not _should_notify(settings.slack_dedup_state_file, stage, detail):
        return

    message = _build_message(
        run_id=run_id,
        timezone=settings.timezone,
        stage=stage,
        stage_label=stage_label,
        summary=summary,
        detail=detail,
        next_action=next_action,
        log_file=settings.log_file,
    )

    # Webhook 送信
    # ・成功 → 送信時刻を状態ファイルに記録
    # ・失敗 → ログに warn のみ（本処理は継続）
    try:
        _post_webhook(settings.slack_webhook_url, message)
        _record_notify(settings.slack_dedup_state_file, stage, detail)
    except Exception as post_exc:  # noqa: BLE001 - 通知失敗は本処理に影響させない
        append_log(settings.log_file, f"warn slack={post_exc}")


def _build_message(
    *,
    run_id: str,
    timezone: str,
    stage: str,
    stage_label: str,
    summary: str,
    detail: str,
    next_action: str,
    log_file: Path,
) -> str:
    """Slack 用の複数行メッセージを組み立てる。"""
    tz = ZoneInfo(timezone)
    timestamp_jst = datetime.now(tz=tz).strftime("%Y-%m-%d %H:%M:%S JST")
    try:
        log_relative = log_file.as_posix()
    except ValueError:
        log_relative = str(log_file)

    return (
        f"[ERROR] 博多混雑RPA — {stage_label}\n"
        f"run_id: {run_id}\n"
        f"時刻: {timestamp_jst}\n"
        f"段階: {stage}\n"
        f"概要: {summary}\n"
        f"詳細: {detail}\n"
        f"exit: 1\n"
        f"次のアクション: {next_action}\n"
        f"ログ: {log_relative}"
    )


def _sanitize(text: str) -> str:
    """Webhook URL・長い ID・パスをマスクして通知本文を安全化する。"""
    sanitized = _SLACK_WEBHOOK_RE.sub("[REDACTED]", text)
    sanitized = _PATH_RE.sub(_redact_path, sanitized)
    sanitized = _LONG_ID_RE.sub("[REDACTED]", sanitized)
    if len(sanitized) > MAX_DETAIL_LEN:
        sanitized = sanitized[: MAX_DETAIL_LEN - 3] + "..."
    return sanitized


def _redact_path(match: re.Match[str]) -> str:
    path = Path(match.group(0))
    return path.name


def _dedup_key(stage: str, detail: str) -> str:
    detail_prefix = detail[:80]
    digest = hashlib.sha256(f"{stage}:{detail_prefix}".encode()).hexdigest()[:16]
    return f"{stage}:{digest}"


def _should_notify(state_file: Path, stage: str, detail: str) -> bool:
    """15分以内に同じエラーを送ったか判定する。送っていなければ True。"""
    key = _dedup_key(stage, detail)
    dedup_state = _load_state(state_file)
    last_sent_raw = dedup_state.get(key)
    # 初回は必ず送る
    if not last_sent_raw:
        return True

    try:
        last_sent = datetime.fromisoformat(last_sent_raw)
    except ValueError:
        return True

    now = datetime.now(tz=UTC)
    if last_sent.tzinfo is None:
        last_sent = last_sent.replace(tzinfo=UTC)
    return now - last_sent >= timedelta(minutes=DEDUP_MINUTES)


def _record_notify(state_file: Path, stage: str, detail: str) -> None:
    """送信成功時刻を状態ファイルに記録する。"""
    key = _dedup_key(stage, detail)
    dedup_state = _load_state(state_file)
    dedup_state[key] = datetime.now(tz=UTC).isoformat(timespec="seconds")
    _save_state(state_file, dedup_state)


def _load_state(state_file: Path) -> dict[str, str]:
    """重複抑制用の JSON 状態を読む。壊れていれば空 dict。"""
    if not state_file.exists():
        return {}
    try:
        state_json = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if isinstance(state_json, dict):
        return {str(k): str(v) for k, v in state_json.items()}
    return {}


def _save_state(state_file: Path, dedup_state: dict[str, str]) -> None:
    """重複抑制用の JSON 状態を書き込む。"""
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(dedup_state, ensure_ascii=False, indent=2), encoding="utf-8")


def _post_webhook(url: str, text: str) -> None:
    """Slack Incoming Webhook に POST する。"""
    response = httpx.post(
        url,
        json={"text": text},
        timeout=POST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
