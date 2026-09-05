# 設定読込（config）

> モード: understand
> 対象: `src/hakata_gym_crowding/config.py`
> 最終更新: 2026-09-05

## やりたいこと

`.env` ファイルから実行に必要な値を読み、パスをプロジェクトルート基準に直して返す。

## コード（D形式・標準形）

```python
# config/.env を読み込む
load_dotenv(環境ファイルパス)

スプレッドシートID = 環境変数("SPREADSHEET_ID")
if Sheets必須 and スプレッドシートIDが空:
    raise ValueError("SPREADSHEET_ID 未設定")

認証ファイル = 環境変数("GOOGLE_APPLICATION_CREDENTIALS")
if 相対パスなら:
    認証ファイル = プロジェクトルート / 認証ファイル

ログファイル = 環境変数("LOG_FILE", 既定="logs/run.log")
if 相対パスなら:
    ログファイル = プロジェクトルート / ログファイル

return Settings(
    spreadsheet_id=スプレッドシートID,
    google_credentials=認証ファイル,
    ...
)
```

## 用語

| 用語 | 意味 |
|---|---|
| .env | 秘密を含む設定を書くファイル（リポジトリには載せない） |
| 環境変数 | プログラム外から渡す設定値の名前と値のペア |

## 対応する実装

| D形式の名前 | 実コードの名前 | ファイル |
|---|---|---|
| Settings | `Settings` | `src/hakata_gym_crowding/config.py` |
| 設定を読む | `load_settings()` | `src/hakata_gym_crowding/config.py` |
