# doc/ai — エージェント知識層

エージェント向けのガイド・セッション記録・意思決定索引を **1 ツリー** に集約する正本です。

実行層（常時制約・手順・短期記憶）は [`.cursor/`](../../.cursor/) にあります。役割分担は [runtime.md](runtime.md) を参照してください。

## ディレクトリ

| パス | 内容 |
|---|---|
| [guidelines/](guidelines/) | Project_map・checklists・既知エラー正本 |
| [sessions/](sessions/) | **意思決定の財産化** — 背景・採用/非採用・検証の本文 |
| [decisions/](decisions/README.md) | sessions・ADR・ABC の横断索引 |
| [runtime.md](runtime.md) | `.cursor` 実行層の説明 |

## 知識の三層

| 層 | パス | 用途 |
|---|---|---|
| **アーカイブ** | [sessions/](sessions/)・[00_開発日誌.md](../specs/00_開発日誌.md) | 全文・時系列の経緯（検索・参照の正本） |
| **索引** | [decisions/README.md](decisions/README.md) | トピック横断で探す |
| **昇格** | [試験実装のエラー.md](guidelines/試験実装のエラー.md)・[doc/adr/](../adr/)・[reference/setup/](../reference/setup/) | 再利用ナレッジ（Phase 1 必読） |

再利用価値のある内容は sessions から昇格層へ移し、sessions には経緯全文を残す。

## 記録の流れ（財産化）

```text
チャット（比較検討・実装）
  → doc/ai/sessions/（本文・経緯の正本）
  → doc/specs/00_開発日誌.md（日次索引）
  → 昇格先（rules / specs / adr / エラー正本）
  → doc/ai/decisions/README.md（トピック索引）
  → .cursor/doc/memory_stream.md（短期ファクトのみ・自動）
```

`sessions/` は **全開発リポジトリ横断の意思決定アーカイブ**。各プロジェクトの記録を [template_sync](../../.cursor/rules/template_sync.mdc) で集約し、PoC 由来の `2026-*.md` も資産として維持する。

## 手順 SKILL

| 状況 | SKILL |
|---|---|
| 実装タスク完了 | [agent-session-record](../../.cursor/skills/agent-session-record/SKILL.md) |
| 設計のみ・比較検討 | [design-decision-record](../../.cursor/skills/design-decision-record/SKILL.md) |
| 既知エラー | [known-error-entry](../../.cursor/skills/known-error-entry/SKILL.md) |
| 短期ファクト（自動） | [memory_logger](../../.cursor/rules/memory_logger.mdc) → `.cursor/doc/memory_stream.md` |

## 索引

詳細な参照先一覧は [guidelines/Project_map.md](guidelines/Project_map.md) を参照。
