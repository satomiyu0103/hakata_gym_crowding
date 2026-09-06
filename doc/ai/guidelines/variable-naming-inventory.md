# 変数命名インベントリ（既存違反・参照用）

最終更新: 2026-09-06

## 運用方針

- **一括リネームはしない**。ファイルを触ったときに、その範囲だけ改善する。
- 新規・変更コードは [naming_conventions.mdc](../../.cursor/rules/naming_conventions.mdc) と [junior-friendly-naming/SKILL.md](../../.cursor/skills/junior-friendly-naming/SKILL.md) に従う。
- stop フック（`check-variable-naming.py`）は **git diff の追加行のみ** 検査する。下表は既存コードの参照用。
- 解消した行は `[x]` に更新する（行は削除しない）。

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

## 関連

- 命名規約: [naming_conventions.mdc](../../.cursor/rules/naming_conventions.mdc)
- 手順: [junior-friendly-naming/SKILL.md](../../.cursor/skills/junior-friendly-naming/SKILL.md)
- すり合わせ計画: [junior-variable-naming-alignment.md](../../doc/specs/plans/junior-variable-naming-alignment.md)

## 将来検討

- ruff / flake8 プラグインによる静的解析（hook 補完）
