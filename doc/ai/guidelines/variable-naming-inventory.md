# 変数命名インベントリ — 博多体育館トレーニング室混雑 RPA

最終更新: 2026-09-06

> **運用方法（テンプレ正本）**: [variable-naming-inventory-ops.md](variable-naming-inventory-ops.md)  
> 本ファイルは **博多体育館プロジェクト固有** の台帳。`publish` では上書きされない。

## プロジェクト語彙（博多固有）

| 語彙 | 意味 |
|---|---|
| `gym` | 体育館エリア（ピープルカウンター JSON の gym セクション） |
| `train` | トレーニング室エリア（train セクション） |
| `crowding` | 混雑状況・人数ベースの判定 |
| `weather` | トレーニング室ページから取得する天気 |
| `snapshot` | 混雑 JSON 取得直後の1件（シート行変換前） |
| `record` | スプレッドシート16列の1行（`CrowdingRecord`） |
| `worksheet` | Google スプレッドシートのシート（タブ） |
| `spreadsheet` | 混雑履歴の保存先スプレッドシート全体 |
| `run_id` | 定期実行の1回を識別する ID（ログ・Slack 通知） |
| `maintenance` | サイトメンテナンス中フラグ |
| `stale` | 計測時刻が5分以上古いデータ |
| `notify` | Slack 障害通知 |
| `schedule` | 開館時間・休館日の実行判定 |

## 違反一覧

| 状態 | 優先度 | ファイル | 現行名 | 推奨名 | 理由 |
|---|---|---|---|---|---|
| [ ] | 高 | `src/hakata_gym_crowding/fetch/pcounter.py` L103 | `data` | `parsed_json` | 禁止語 `data` |
| [ ] | 高 | `src/hakata_gym_crowding/fetch/pcounter.py` L104 | `node` | `hakata_section_json` | 単体では何の JSON か不明 |
| [ ] | 高 | `src/hakata_gym_crowding/fetch/pcounter.py` L137 | `payload` | `parsed_response_json` | 型名 `PCounterPayload` と混同 |
| [ ] | 中 | `src/hakata_gym_crowding/domain/crowding.py` L23 | `count`（引数） | `occupant_count` | 単体では何の人数か不明 |
| [ ] | 中 | `src/hakata_gym_crowding/notify/slack.py` | `state` | `dedup_state` | 通知文脈が名前に無い |
| [ ] | 中 | `src/hakata_gym_crowding/notify/slack.py` | `payload` | `state_json` | 汎用名 |
| [ ] | 中 | `src/hakata_gym_crowding/domain/record_format.py` L64 | `weather_data` | `resolved_weather` | `_data` 接尾辞が汎用 |
| [ ] | 低 | `src/hakata_gym_crowding/cli.py` L142 | `line` | `status_summary_line` | 内容が名前に無い |

## 例外（維持）

| ファイル | 名前 | 理由 |
|---|---|---|
| `src/hakata_gym_crowding/domain/models.py` | `PCounterPayload.count` | 外部 JSON フィールド境界。パース後は `train_count` / `gym_count` に昇格 |
| `src/hakata_gym_crowding/cli.py` | `args` | argparse 慣習（許容リスト） |

## 良い例（踏襲）

| ファイル | 名前 | パターン |
|---|---|---|
| `cli.py` | `weather_fetch_failed` | `{対象}_{状態}` |
| `cli.py` | `snapshot` | ドメイン語（取得直後1件） |
| `domain/models.py` | `train_count`, `gym_count` | `{場所}_{属性}` |
| `domain/record_format.py` | `build_crowding_record` | `{動詞}_{対象}` |
| `notify/slack.py` | `notify_settings` | `{用途}_{対象}` |

## 関連

- 運用: [variable-naming-inventory-ops.md](variable-naming-inventory-ops.md)
- 命名規約: [naming_conventions.mdc](../../../.cursor/rules/naming_conventions.mdc)
- 手順: [junior-friendly-naming/SKILL.md](../../../.cursor/skills/junior-friendly-naming/SKILL.md)
- すり合わせ: [junior-variable-naming-alignment.md](../../specs/plans/junior-variable-naming-alignment.md)

## 将来検討

- ruff / flake8 プラグインによる静的解析（hook 補完）
