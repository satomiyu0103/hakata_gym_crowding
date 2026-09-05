"""Slack Incoming Webhook による ERROR 通知。"""

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
    """ERROR 通知を Slack へ送る。失敗しても例外は出さない。"""
    if not settings.slack_notify_enabled or not settings.slack_webhook_url:
        return

    stage_label, summary, next_action = STAGE_META[stage]
    detail = _sanitize(str(exc))
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
    key = _dedup_key(stage, detail)
    state = _load_state(state_file)
    last_sent_raw = state.get(key)
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
    key = _dedup_key(stage, detail)
    state = _load_state(state_file)
    state[key] = datetime.now(tz=UTC).isoformat(timespec="seconds")
    _save_state(state_file, state)


def _load_state(state_file: Path) -> dict[str, str]:
    if not state_file.exists():
        return {}
    try:
        payload = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if isinstance(payload, dict):
        return {str(k): str(v) for k, v in payload.items()}
    return {}


def _save_state(state_file: Path, state: dict[str, str]) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _post_webhook(url: str, text: str) -> None:
    response = httpx.post(
        url,
        json={"text": text},
        timeout=POST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
