# Python / uv 環境構築（任意スタック）

> **位置づけ**: ルートテンプレートは言語非依存です。Python を採用する場合のみ本手順に従い `pyproject.toml` と `src/` を初期化してください。

## 概要

`uv` を用いた Python 開発環境のセットアップ手順。主に Windows（PowerShell）向けに記載し、補足で Unix/macOS も示します。

## 前提

- プロジェクトルートに `pyproject.toml` を用意すること（`uv init` または手動作成）
- Python 3.10 以上
- `uv` CLI（未導入なら下記でインストール）

## uv のインストール

PowerShell:

```powershell
python -m pip install --upgrade pip
python -m pip install uv
```

Unix/macOS:

```bash
python -m pip install --upgrade pip
python -m pip install uv
```

## 仮想環境と開発インストール

プロジェクトルートで実行:

```powershell
uv venv
uv pip install -e .
```

## 依存の追加

```powershell
uv pip install requests
git add pyproject.toml uv.lock
git commit -m "deps: add requests"
```

## テスト実行（pytest 採用時の例）

```powershell
uv pip install pytest
uv run pytest tests/unit -v
```

## ビルドバックエンド（hatchling）

`uv sync` 後にパッケージがインポートできない場合、`pyproject.toml` に `[build-system]` が無いことが多い。`hatchling` を採用する。

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/{{APP_DIR}}"]

[tool.uv]
package = true
```

`{{APP_DIR}}` は実パッケージ名に置き換える。

## 日時（timezone-aware）

外部 API が ISO 8601 + UTC を要求する場合、naive datetime は比較エラーの原因になる。プロジェクト内では UTC-aware のみを扱う。

```python
from datetime import datetime, timezone

dt = datetime.now(timezone.utc)  # 推奨
# datetime.now() / datetime.utcnow() は使用しない
```

## トラブルシューティング

- `pyproject.toml` が無い: ルートで `uv init` を実行するか、手動で作成する
- PowerShell の文字化け: `Out-File -Encoding utf8` または Python の `Path.write_text(..., encoding='utf-8')` を使う
