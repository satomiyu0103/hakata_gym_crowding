"""実行設定の読み込み。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    spreadsheet_id: str
    google_credentials: Path
    timezone: str
    sheet_name: str
    log_file: Path


def load_settings(env_file: Path | None = None, *, require_sheets: bool = True) -> Settings:
    """`.env` から設定を読み込む。"""
    if env_file is None:
        env_file = PROJECT_ROOT / "config" / ".env"
    load_dotenv(env_file)

    spreadsheet_id = os.getenv("SPREADSHEET_ID", "").strip()
    if require_sheets and not spreadsheet_id:
        msg = "SPREADSHEET_ID が未設定です。config/.env.example を参照してください。"
        raise ValueError(msg)

    credentials_raw = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS",
        "config/service-account.json",
    ).strip()
    credentials_path = Path(credentials_raw)
    if not credentials_path.is_absolute():
        credentials_path = PROJECT_ROOT / credentials_path

    log_file_raw = os.getenv("LOG_FILE", "logs/run.log").strip()
    log_file = Path(log_file_raw)
    if not log_file.is_absolute():
        log_file = PROJECT_ROOT / log_file

    return Settings(
        spreadsheet_id=spreadsheet_id,
        google_credentials=credentials_path,
        timezone=os.getenv("TIMEZONE", "Asia/Tokyo").strip(),
        sheet_name=os.getenv("SHEET_NAME", "混雑履歴").strip(),
        log_file=log_file,
    )
