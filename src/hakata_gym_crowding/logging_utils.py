"""実行ログの書き込み。

含まれるもの:
- append_log — logs/run.log へ1行追記

処理の流れ:
1. ログファイルの親フォルダを作成（無ければ）
2. タイムスタンプ付きで1行追記（既存行は消さない）
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


def append_log(log_file: Path, message: str) -> None:
    """1 行追記する。

    受け取る: ログファイルパス、メッセージ文字列
    返す: なし（副作用: ファイル末尾に1行追加）
    """
    # logs/ など親フォルダが無ければ先に作成する
    log_file.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 追記モードで1行書く（既存ログは消さない）
    with log_file.open("a", encoding="utf-8") as handle:
        handle.write(f"{timestamp}\t{message}\n")
