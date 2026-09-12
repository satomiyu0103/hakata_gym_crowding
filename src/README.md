# hakata_gym_crowding（ソース）

博多体育館トレーニング室の混雑状況を定期取得し、Google スプレッドシートへ追記する RPA の Python パッケージです。

## 責務

p-counter 公開 JSON とトレーニング室ページ HTML から混雑・天気を取得し、開館時間・休館日を判定したうえで「混雑履歴」シートへ 16 列で 1 行追記する。

## 入口

| ファイル | 役割 |
|---|---|
| `hakata_gym_crowding/cli.py` | CLI エントリ（GitHub Actions / 手動実行） |
| `scripts/migrate_sheet_columns.py` | 旧 6 列シート → 新 16 列への一度きり移行 |

## モジュール構成

```
hakata_gym_crowding/
├── cli.py              # 設定読込 → 開館判定 → 取得 → Sheets 追記
├── config.py           # .env 読み込み
├── logging_utils.py    # logs/run.log 追記
├── domain/             # モデル・混雑ラベル・行組立
├── fetch/              # p-counter JSON・training ページ天気
├── schedule/           # ScheduleGuard（9:00–22:00・休館日）
├── store/              # Google Sheets 書き込み
└── notify/             # Slack ERROR 通知（FR-LOG-002）
```

## 依存先

| 外部 | 用途 |
|---|---|
| p-counter JSON ×2 | 混雑人数・計測時刻 |
| ssk-hakata-gym.com/training/ | 天気 6 項目（HTML） |
| Google Sheets API | 履歴保存 |
| Slack Incoming Webhook | ERROR 通知（任意） |
| `config/.env` | スプレッドシート ID・認証 JSON パス・Webhook URL |

## ローカル実行

```powershell
uv sync
uv run python -m hakata_gym_crowding.cli --dry-run --force
uv run python -m hakata_gym_crowding.cli
```

詳細: [doc/reference/setup/google-sheets-hakata-crowding.md](../doc/reference/setup/google-sheets-hakata-crowding.md) · [Slack 通知](../doc/reference/setup/slack-webhook-hakata-crowding.md)
