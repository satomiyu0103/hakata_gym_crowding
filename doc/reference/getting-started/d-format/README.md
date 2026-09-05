# D形式解説 一覧

博多混雑 RPA のソースコードを、日本語変数と行コメントで読み解くための解説集。

読み方の手順: [読み方.md](../読み方.md)

| ファイル | D形式解説 | 実装パス |
|---|---|---|
| CLI メイン処理 | [cli-main-flow.md](cli-main-flow.md) | `src/hakata_gym_crowding/cli.py` |
| 設定読込 | [config-settings.md](config-settings.md) | `src/hakata_gym_crowding/config.py` |
| 開館・休館判定 | [schedule-guard.md](schedule-guard.md) | `src/hakata_gym_crowding/schedule/guard.py` |
| 混雑 JSON 取得 | [fetch-pcounter.md](fetch-pcounter.md) | `src/hakata_gym_crowding/fetch/pcounter.py` |
| 天気 HTML 取得 | [fetch-training-page.md](fetch-training-page.md) | `src/hakata_gym_crowding/fetch/training_page.py` |
| スプレッドシート追記 | [store-sheets.md](store-sheets.md) | `src/hakata_gym_crowding/store/sheets.py` |
| Slack 通知 | [notify-slack.md](notify-slack.md) | `src/hakata_gym_crowding/notify/slack.py` |
| 通知パッケージ | [notify-init.md](notify-init.md) | `src/hakata_gym_crowding/notify/__init__.py` |
| レコード組立 | [domain-record-format.md](domain-record-format.md) | `src/hakata_gym_crowding/domain/record_format.py` |
| ドメインモデル | [domain-models.md](domain-models.md) | `src/hakata_gym_crowding/domain/models.py` |
| 混雑ラベル | [domain-crowding.md](domain-crowding.md) | `src/hakata_gym_crowding/domain/crowding.py` |
| 実行ログ | [logging-utils.md](logging-utils.md) | `src/hakata_gym_crowding/logging_utils.py` |

作成手順: [d-format-code-guide](../../../../.cursor/skills/d-format-code-guide/SKILL.md)
