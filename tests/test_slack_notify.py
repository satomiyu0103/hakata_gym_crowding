"""Slack ERROR 通知のテスト。"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx

from hakata_gym_crowding.config import Settings
from hakata_gym_crowding.notify import slack as slack_module
from hakata_gym_crowding.notify.slack import (
    _build_message,
    _sanitize,
    _should_notify,
    notify_error,
)


def _settings(
    tmp_path: Path,
    *,
    webhook_url: str = "https://hooks.slack.com/services/T00/B00/XXX",
    enabled: bool = True,
) -> Settings:
    log_file = tmp_path / "logs" / "run.log"
    return Settings(
        spreadsheet_id="sheet-id",
        google_credentials=tmp_path / "config" / "service-account.json",
        timezone="Asia/Tokyo",
        sheet_name="混雑履歴",
        log_file=log_file,
        slack_webhook_url=webhook_url,
        slack_notify_enabled=enabled,
        slack_dedup_state_file=log_file.parent / ".slack_notify_state.json",
    )


def test_notify_error_skips_when_webhook_url_empty(tmp_path: Path) -> None:
    settings = _settings(tmp_path, webhook_url="")

    with patch.object(slack_module, "_post_webhook") as mock_post:
        notify_error(settings, run_id="run-1", stage="fetch", exc=RuntimeError("fail"))

    mock_post.assert_not_called()


def test_build_message_contains_stage_and_next_action(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    message = _build_message(
        run_id="20260905-143012-a1b2",
        timezone=settings.timezone,
        stage="fetch",
        stage_label="混雑取得",
        summary="p-counter JSON の取得に失敗",
        detail="JSON 取得に失敗しました",
        next_action="ネットワーク確認",
        log_file=settings.log_file,
    )

    assert "[ERROR] 博多混雑RPA — 混雑取得" in message
    assert "run_id: 20260905-143012-a1b2" in message
    assert "段階: fetch" in message
    assert "次のアクション: ネットワーク確認" in message
    assert "logs/run.log" in message


def test_sanitize_redacts_slack_webhook_url() -> None:
    text = "failed https://hooks.slack.com/services/T00/B00/secret token"
    assert "[REDACTED]" in _sanitize(text)
    assert "hooks.slack.com" not in _sanitize(text)


def test_sanitize_truncates_long_detail() -> None:
    text = "JSON 取得に失敗しました: " + ("detail " * 80)
    sanitized = _sanitize(text)
    assert len(sanitized) == 500
    assert sanitized.endswith("...")


@patch("hakata_gym_crowding.notify.slack.httpx.post")
def test_notify_error_posts_to_webhook(mock_post: MagicMock, tmp_path: Path) -> None:
    mock_post.return_value = MagicMock(status_code=200, raise_for_status=MagicMock())
    settings = _settings(tmp_path)

    notify_error(settings, run_id="run-1", stage="sheets", exc=RuntimeError("write failed"))

    mock_post.assert_called_once()
    payload = mock_post.call_args.kwargs["json"]
    assert payload["text"].startswith("[ERROR] 博多混雑RPA — Sheets 書込")


@patch("hakata_gym_crowding.notify.slack.httpx.post")
def test_notify_error_swallows_post_failure(mock_post: MagicMock, tmp_path: Path) -> None:
    mock_post.side_effect = httpx.HTTPError("network down")
    settings = _settings(tmp_path)

    notify_error(settings, run_id="run-1", stage="fetch", exc=RuntimeError("fetch failed"))

    assert settings.log_file.exists()
    log_text = settings.log_file.read_text(encoding="utf-8")
    assert "warn slack=" in log_text


def test_should_notify_deduplicates_within_window(tmp_path: Path) -> None:
    state_file = tmp_path / ".slack_notify_state.json"
    stage = "fetch"
    detail = "same failure"

    assert _should_notify(state_file, stage, detail) is True
    state_file.write_text(
        json.dumps(
            {
                slack_module._dedup_key(stage, detail): (
                    datetime.now(tz=UTC) - timedelta(minutes=5)
                ).isoformat(timespec="seconds")
            }
        ),
        encoding="utf-8",
    )

    assert _should_notify(state_file, stage, detail) is False


def test_should_notify_allows_after_dedup_window(tmp_path: Path) -> None:
    state_file = tmp_path / ".slack_notify_state.json"
    stage = "fetch"
    detail = "same failure"

    state_file.write_text(
        json.dumps(
            {
                slack_module._dedup_key(stage, detail): (
                    datetime.now(tz=UTC) - timedelta(minutes=20)
                ).isoformat(timespec="seconds")
            }
        ),
        encoding="utf-8",
    )

    assert _should_notify(state_file, stage, detail) is True
