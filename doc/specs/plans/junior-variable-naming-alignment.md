# ジュニア向け変数命名規則 — すり合わせ計画

> ステータス: **完了**（2026-09-06）— **案 B 採用**（命名規約強化 + Rule/Skill/Hook 整備。既存コード一括リネームはしない）  
> 種別: 運用・ドキュメント

## 決定内容

| 項目 | 決定 |
|---|---|
| 採用案 | **B. 命名規約の強化**（英語 `snake_case` 維持） |
| 対象パス | `src/`, `tests/`, `scripts/` |
| 既存リネーム | **しない**（触ったときだけ改善。一覧は inventory） |
| 日本語識別子（案 D） | **不採用** — D形式は学習用のまま |

## 背景

2026-09-05 に **ジュニア向けコメント三層モデル（L1/L2/L3）** と **D形式解説12本** を整備した。

| 層 | 識別子の言語 | 正本 |
|---|---|---|
| `src/` 実装 | 平易な **英語**（`snake_case`） | [naming_conventions.mdc](../../../.cursor/rules/naming_conventions.mdc) |
| D形式解説 | **日本語**変数（学習用） | [d-format-code-guide](../../../.cursor/skills/d-format-code-guide/SKILL.md) |
| コメント | **日本語** | [code_comments.mdc](../../../.cursor/rules/code_comments.mdc) |

## 成果物（完了）

| 成果物 | パス |
|---|---|
| 命名 Rule 拡張 | [naming_conventions.mdc](../../../.cursor/rules/naming_conventions.mdc) |
| 命名 Skill | [junior-friendly-naming/SKILL.md](../../../.cursor/skills/junior-friendly-naming/SKILL.md) |
| stop フック | [check-variable-naming.py](../../../.cursor/hooks/check-variable-naming.py) · [stop-variable-naming-followup.ps1](../../../.cursor/hooks/stop-variable-naming-followup.ps1) |
| 既存違反一覧 | [variable-naming-inventory.md](../../ai/guidelines/variable-naming-inventory.md) |
| ディレクトリ構成 | [05_ディレクトリ構成.md](../05_ディレクトリ構成.md) 命名節 |
| 運用配線 | `agent_implement_entry`, `dev_auto_ops`, `phase2`, `junior_code_reading`, `AGENTS.md` |

## すり合わせの論点（記録）

### 1. 方針の選択肢

| 案 | 結果 |
|---|---|
| **A. 現状維持** | 不採用 |
| **B. 命名規約の強化** | **採用** |
| **C. 限定的リネーム** | 将来・触ったときのみ |
| **D. 日本語識別子** | 不採用 |

### 2. 決定済み項目

- [x] 採用案: B
- [x] 対象パス: `src/` + `tests/` + `scripts/`
- [x] 禁止語・推奨語: rule / skill に具体化（`gym_count` パターンを正とする）
- [x] 既存 FR・CLI・Sheets 列名: 変更しない
- [x] D形式対応表: リネーム時に手動更新（inventory 参照）

## 関連

- 完了: [07_CHANGELOG.md](../07_CHANGELOG.md) Unreleased
- ROADMAP: [06_ROADMAP.md](../06_ROADMAP.md) バックログ
