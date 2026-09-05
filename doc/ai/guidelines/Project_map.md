# プロジェクトマップ（AIエージェント向け）

**{{PROJECT_DESCRIPTION}}**

AI エージェントが短時間で要件・設計・運用ルールを把握できるように、参照先を整理しています。

> **行動規範**: [`.cursor/rules/agent_core.mdc`](../../../.cursor/rules/agent_core.mdc)（常時） / [`.cursor/rules/agent_implement_entry.mdc`](../../../.cursor/rules/agent_implement_entry.mdc)（実装時） / [`.cursor/skills/phase3-doc-updates/SKILL.md`](../../../.cursor/skills/phase3-doc-updates/SKILL.md)（Phase 3 詳細）

## まず読むべき 4 ファイル（Phase 1）

1. `doc/ai/README.md` — 知識層の入口（sessions 財産化の流れ）
2. `doc/specs/02_要件定義.md` — 実装範囲（MoSCoW）と非機能要件（FR/NFR コード）
3. `doc/specs/04_機能一覧.md` — 全機能の実装状況と採番ルール
4. `doc/ai/guidelines/試験実装のエラー.md` — 既知エラーと再発防止策

---

## 機能コード体系（FR / NFR）

> 詳細は `doc/specs/04_機能一覧.md` の「採番ルール」セクションを参照。

```
[TYPE]-[CATEGORY]-[NNN]

TYPE:  FR = 機能要件  /  NFR = 非機能要件

CATEGORY（FR 用）: {{CATEGORY_CODE_1}} 等 — プロジェクトで定義

CATEGORY（NFR 用）:
  SEC   = セキュリティ
  PERF  = パフォーマンス
  OPS   = 運用・保守

NNN: カテゴリ内の連番（001〜）。欠番は振り直さない。
```

---

## 意思決定の財産化

| 層 | パス | 内容 |
|---|---|---|
| 本文 | `doc/ai/sessions/` | 背景・採用/非採用・検証（**全リポジトリ横断アーカイブ**。`template_sync` で集約） |
| 索引 | `doc/specs/00_開発日誌.md` | 日次 3〜10 行 + リンク |
| 横断 | `doc/ai/decisions/README.md` | トピック別 1 行 |
| 短期 | `.cursor/doc/memory_stream.md` | キーワードファクト |

手順: [agent-session-record](../../../.cursor/skills/agent-session-record/SKILL.md) / [design-decision-record](../../../.cursor/skills/design-decision-record/SKILL.md)

---

## .cursor 構成（エージェント正本）

```text
.cursor/
├─ rules/
├─ skills/
│  ├─ implementation-phase1/ phase2/ phase3-doc-updates/
│  ├─ task-value-first/
│  ├─ agent-session-record/ design-decision-record/
│  └─ audit-* / changelog-entry / …
└─ doc/
   └── memory_stream.md
```

## doc ディレクトリ構造

```text
doc/
├─ ai/
│  ├─ README.md
│  ├─ sessions/          ← 意思決定本文（財産化）
│  ├─ decisions/
│  └─ guidelines/
├─ reference/
│  ├─ getting-started/
│  ├─ setup/             ← スタック別（python-uv / django / gas 等）
│  └─ cheatsheets/
├─ specs/
├─ templates/
└─ adr/
```

---

## AI エージェント向け参照ガイド

| やりたいこと | 参照先 |
|---|---|
| 要件確認 | `doc/specs/02_要件定義.md` |
| 検証設計・MVP 前 QA ゲート | `doc/specs/08_検証設計.md` · `doc/ai/guidelines/checklists/qa_gate.md` |
| Windows デスクトップ MVP 要件ゲート | `doc/ai/guidelines/desktop-windows-mvp-spec-gates.md` · `qa_gate.md` §H |
| 機能コード・実装状況 | `doc/specs/04_機能一覧.md` |
| 設計・フロー確認 | `doc/specs/03_システム設計.md` |
| ディレクトリ構成 | `doc/specs/05_ディレクトリ構成.md` |
| 過去のエラーと対策 | `doc/ai/guidelines/試験実装のエラー.md` |
| 意思決定の横断索引 | `doc/ai/decisions/README.md` |
| セッション記録の目的 | `doc/ai/sessions/README.md` |
| スタック別セットアップ | `doc/reference/setup/`（python-uv / django / gas-clasp-pnpm / gas-operations / google-drive-mcp 等） |
| Google Drive MCP 運用（個人情報参照） | `.cursor/skills/gdrive-mcp/SKILL.md` → `doc/ai/guidelines/google-drive-mcp.md` |
| Google Drive MCP セットアップ | `doc/reference/setup/google-drive-mcp.md` |
| やりたいこと・コード理解（D形式） | `.cursor/skills/d-format-code-guide/SKILL.md` → `doc/reference/getting-started/d-format/` |
| タスク価値検証・差分計画 | `.cursor/skills/task-value-first/SKILL.md` → `doc/ai/guidelines/task-value-first.md` |
| 過去セッション全文 | `doc/ai/sessions/` |
| ADR | `doc/adr/` |
| Agent 憲法（常時） | `.cursor/rules/agent_core.mdc` |
| Phase 1〜3 手順 | `.cursor/skills/implementation-phase1/` 〜 `phase3-doc-updates/` |
| 記憶ストリーム | `.cursor/doc/memory_stream.md` |
