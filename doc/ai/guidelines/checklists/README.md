# 定期監査チェックリスト（索引）

最終更新: 2026-08-16

> **正本**: 原則・例外・トレードオフは `.cursor/rules/` と `.cursor/skills/` に書く。  
> 本フォルダは **観察可能な Yes/No** の検証項目のみ。判断が必要なときは各項目の「根拠」リンク先を読む。

## 置き場所（2026-08-16 変更）

大分類チェックリストは **各 `audit-*` Skill 配下の `references/`** に移動した。Skill と参照資料の距離を縮めるため（Anthropic Agent Skills の bundled resources に合わせる）。本フォルダには **Skill を持たない** `qa_gate.md` と本索引のみ残る。

## いつ使うか

| タイミング | 使うファイル |
|---|---|
| **MVP 着手前**（要件・設計確定後） | [qa_gate.md](qa_gate.md) |
| プロトタイプ完成後の総点検 | [audit-post-prototype/references/post_prototype_audit.md](../../../../.cursor/skills/audit-post-prototype/references/post_prototype_audit.md) |
| 不定期リファクタ・設計見直し前後 | [audit-refactor-full/references/refactor_audit.md](../../../../.cursor/skills/audit-refactor-full/references/refactor_audit.md) |
| カテゴリ単体の棚卸し | 下表の大分類ファイル |

**通常の実装・PR 時**は Phase 1〜2 の Skills を読む。本フォルダは **常時必読にしない**（[`.cursor/rules/agent_implement_entry.mdc`](../../../../.cursor/rules/agent_implement_entry.mdc) 参照）。

## 大分類一覧

| 大分類 | ファイル | 呼び出す Skill |
|---|---|---|
| QA ゲート（MVP 前） | [qa_gate.md](qa_gate.md) | （Skill なし・[08_検証設計.md](../../../specs/08_検証設計.md) が根拠） |
| セキュリティ | [security.md](../../../../.cursor/skills/audit-security/references/security.md) | `audit-security` |
| 実装・品質 | [implementation.md](../../../../.cursor/skills/audit-implementation/references/implementation.md) | `audit-implementation` |
| 運用・バッチ | [operations.md](../../../../.cursor/skills/audit-operations/references/operations.md) | `audit-operations` |
| リファクタリング | [refactoring.md](../../../../.cursor/skills/audit-refactoring/references/refactoring.md) | `audit-refactoring` |
| ドキュメント・完了 | [documentation.md](../../../../.cursor/skills/audit-documentation/references/documentation.md) | `audit-documentation` |

## AI への渡し方（例）

Skill 名を指定すれば、チェックリストのパスは Skill 側が知っている。

```text
audit-refactor-full に従って監査してください。
```

## 同期時の扱い

移動先の `references/*.md` は `.cursor/skills/`（テンプレ所有・上書き）配下にあるが、**チェック状態と実施記録をプロジェクトが持つ** ため、[sync-manifest.json](../../../../sync-manifest.json) で `exclude`（上書き禁止）＋ `copy_if_missing`（初回のみ配布）に登録している。テンプレ更新でプロジェクトの記録が消えない。

## 既存プロジェクトの移行

`dev-template-sync` を適用すると、新パスに **雛形** が配られる。旧パス `doc/ai/guidelines/checklists/*.md` の記入済みファイルは削除されないので、プロジェクトごとに手で移してから旧ファイルを消す。

## 実施記録（任意）

監査実施時は、該当チェックリスト末尾の「実施記録」に日付・実施者・未達の要約を追記する。

## 変更履歴

### 2026-08-16 — 大分類チェックリストを audit-* Skill 配下へ移動

- **理由**: 参照元 Skill との距離が遠く、`SKILL.md` から `doc/ai/guidelines/checklists/` を辿る構造だった。Anthropic Agent Skills の bundled resources（`references/`）方針に合わせる。
- **以前**: 本フォルダに 8 ファイル（`qa_gate.md` / `security.md` / `implementation.md` / `operations.md` / `refactoring.md` / `documentation.md` / `post_prototype_audit.md` / `refactor_audit.md`）を並置し、各 `audit-*` SKILL.md がフルパスで参照していた。
- **操作**: 7 ファイルを `.cursor/skills/audit-*/references/` へ移動。相対リンクを新しい深さへ書き換え。本 README を索引スタブ化。`sync-manifest.json` に上書き禁止と初回配布を追記。`qa_gate.md` は対応 Skill が無いため現状維持。
