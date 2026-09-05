"""実行ログの書き込み。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


def append_log(log_file: Path, message: str) -> None:
    """1 行追記する。"""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with log_file.open("a", encoding="utf-8") as handle:
        handle.write(f"{timestamp}\t{message}\n")
