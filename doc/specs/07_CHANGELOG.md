# CHANGELOG

このプロジェクトへの変更はすべてこのファイルに記録する。
形式は [Keep a Changelog](https://keepachangelog.com/ja/1.0.0/) に基づく。
バージョン形式: `v年.マイルストーン番号`（例: `v2026.1`）

機能コードの詳細は [04_機能一覧.md](04_機能一覧.md) を参照。

---

## [Unreleased]

### Added
- `FR-SCHED-001` 手動実行 — `scripts/run_hakata_crowding.bat`（正本）とデスクトップ `RPA` ショートカット作成用 `create_desktop_shortcuts.ps1`
- `FR-FETCH-002` 天気取得 — トレーニング室ページ HTML から天気・最高/最低気温・風速・風向・降水確率を取得
- `FR-STORE-002` 列スキーマ拡張 — 混雑履歴を日本語16列に変更（取得時間＋計測時間）、旧6列移行スクリプト
- `FR-LOG-002` 障害 Slack 通知 — ERROR 時（設定・混雑取得・Sheets 書込）に Incoming Webhook へ送信、15 分重複抑制

### Changed
- `refactor` 変数命名段階修正 — inventory 11件をモジュール単位でリネーム（pcounter / domain / slack / cli / sheets / test）。pytest 36 件 pass、台帳全行 `[x]`
- `docs` 変数命名インベントリ運用 — 汎用正本 `variable-naming-inventory-ops.md`（テンプレ overwrite）とプロジェクト台帳 `variable-naming-inventory.md`（exclude）の二層化。博多固有語彙・違反8件・例外2件を台帳に記載。ai-agent v2026.9 / ds v2026.5 へ配布
- `docs` ジュニア向け変数命名 — `naming_conventions` 拡張、`junior-friendly-naming` Skill、`check-variable-naming.py` stop フック、既存違反 inventory（一括リネームなし）
- `docs` ジュニア向けコメント三層モデル（L1/L2/L3）— 全12 `src/` モジュールに処理の流れ・分岐・例外コメント整備、`junior_code_reading` Rule・`junior-code-reading` Skill、D形式解説12本（`doc/reference/getting-started/d-format/`）、`読み方.md`・`コード解説.md` 索引
- `docs` Phase 2.0 残タスク — `08_検証設計.md` 実データ化、`src/README.md` 拡充、全 `src/` にジュニア向けブロックコメント

### Fixed
- `FR-STORE-002` 列移行 — 旧行の日時・人数・ステータス不正時に行単位でスキップし移行全体を継続
- `FR-SCHED-001` ScheduleGuard — 振替火曜を yesterday 基準に変更、`_third_monday` に月境界ガード
- `FR-FETCH-001` PCounterFetcher — naive datetime を Asia/Tokyo として stale 判定
- `FR-STORE-001` SheetsWriter — `gspread.Worksheet.update` の引数順を修正（`values` 先行）

### Added
- `FR-FETCH-001` `FR-STORE-001` `FR-SCHED-001` `FR-LOG-001` 混雑取得 MVP — p-counter JSON 取得、Google Sheets 追記、ScheduleGuard、CLI、pytest、セットアップ doc

- `docs` 4 層コードコメント規約 — `readable-code-comments` Skill・`doc/ai/guidelines/readable-code-comments.md`・`check-code-comments.py` / `stop-code-comments-followup.ps1` stop フック。`code_comments.mdc`・`junior-code-comments` を拡張
- `docs` Windows デスクトップ MVP 要件ゲート — `desktop-windows-mvp-spec-gates.md` 新設、`qa_gate.md` §H、`試験実装のエラー.md` デスクトップ 3 件、`decisions` 索引。由来: 業務プロジェクト MVP 実機 FB（[sessions/2026-08-15_desktop-mvp-feedback-spec-lessons.md](doc/ai/sessions/2026-08-15_desktop-mvp-feedback-spec-lessons.md)）
- `chore` `.gitignore` に AI Agent / Cursor 除外ブロックを追加 — 公開向け Git 管理のため `.cursor/`・`AGENTS.md`・`doc/ai/sessions/` 等を除外。`sync-manifest.json` の `overwrite` に `.gitignore` を追加し `dev-template-sync` で各プロジェクトへ配布可能に
- `docs` `08_検証設計.md` 新設 — MVP 前の AC・デシジョンテーブル・状態遷移（マトリクス+一覧ハイブリッド）・検証マトリクス。`qa_gate.md` チェックリスト同梱
- `docs` OWASP Agentic Top 10 防御系 Skills 同梱 — `agent-governance`・`agent-owasp-compliance`・`mcp-security-audit`・`owasp-agentic`・`llm-security` を `.cursor/skills/` に配置。`audit-security` から ASI スキャンを先行。`skills-lock.json` 追加
- `docs` `NFR-OPS-003` `japanese-chat-mary` Skill 改訂 — ロールプレイ・お嬢様口調を廃止し、です・ます調の一貫を最優先に
- `docs` `NFR-OPS-003` `japanese-chat-mary` Skill 新設 — チャット口調（メアリ・インスパイア）。`japanese-chat-marie` からリネーム
- `docs` `NFR-OPS-002` Google Drive MCP 運用基盤 — `gdrive-mcp` Skill・`gdrive_mcp_core` Rule・setup/guideline 新設。個人情報正本は Drive、リポジトリは索引のみ（dylancaponi/gdrive-mcp-server + readonly）
- `docs` `NFR-OPS-002` `task-value-first` Skill 新設 — 価値検証・差分計画。`engineer_signals_core` Rule、`agent-session-record` に学び節追加
- `docs` `d-format-code-guide` Skill 新設 — やりたいこと整理・コード理解依頼時に D形式解説を `doc/reference/getting-started/d-format/` へ作成。サンプル `loop-multiply-by-ten.md` 付き
- `docs` `NFR-OPS-002` テンプレ整合・知識アーカイブ統合 — 二役割・三層知識の明文化、重複統合、昇格 doc 新設、壊れリンク修復、rules 汎用化
- `docs` 新設: `adr/0003-gas-runtime.md`、`reference/setup/gas-operations.md`・`product-schema-design.md`、`reference/migration/meishi-to-product.md`、`templates/TPL_引継ぎ資料.md`
- `docs` `試験実装のエラー.md` に GAS サイドバー・期限重複エラーを sessions から昇格
- `docs` `06_ROADMAP.md` に PoC アーカイブ節、`01_ABC` に GAP-A-001 実データ化
- `docs` テンプレートを言語非依存化 — `pyproject.toml`・Python パッケージ雛形・`setup_env` スクリプトを削除。スタック手順は `doc/reference/setup/` へ集約
- `docs` `doc/ai/sessions/README.md` — 全リポジトリ横断アーカイブの位置づけを明文化（PoC 由来 sessions は維持）
- `docs` ADR 0001/0002 を `python-uv.md` へ統合。`django-ui-changes` Skill 削除

### Changed
- `docs` 重複ドキュメント削除（旧パス・索引スタブ 6 件・`agent_workflows.mdc`）。正本は `doc/ai/` と `.cursor/` のみ
- `docs` `template_sync` に同期義務（同一ターン内・省略不可）を明文化。`agent_core`・Phase 2/3 Skills を更新

### Changed

- `docs` `doc/ai/` にエージェント知識層を統合（guidelines・sessions・decisions）。`design-decision-record` SKILL 新設

### Added
- `docs` `doc/ai_guidelines/checklists/` — 大分類別チェックリスト（security / implementation / operations / refactoring / documentation）とプロトタイプ後・リファクタ監査入口

### Changed
- `docs` `workspace_boundary.mdc` を新設しワークスペース外・別プロジェクトへの逸脱を禁止（`agent_core.mdc`・`AGENTS.md`）
- `docs` `japanese-tech-writing` Skill と `japanese_tech_writing.mdc`（適用タイミング）を追加。`ATTRIBUTION.md` で出典明記
- `docs` memory_stream・agent_sessions・開発日誌索引をテンプレへ同時同期する方針に変更
- `docs` 「終了」等のセッション完了時に commit/push まで行う締め手順を memory_logger に追加
- `docs` ログ更新時のテンプレ同期方針を `template_sync`・`memory_logger`・Phase 3 Skill に追記。`doc/records/` 雛形を追加
- `docs` `documentation_wording.mdc` を新設し「人間」「人向け」表記を「利用者」「開発者」等へ置換
- `docs` `memory_logger.mdc`・`template_sync.mdc` と `.cursor/doc/memory_stream.md` を新設（タスク完了時のファクト追記・テンプレ同期方針）
- `docs` `doc/ai_guidelines` ガイド正本を `.cursor/rules`（12 mdc）・`.cursor/skills`（17 Skill）へ再配置。doc は索引スタブ、`agent_implement.mdc` → `agent_implement_entry.mdc`
- `docs` `doc/ai_guidelines/実装規約.md` — コード意図・処理内容のコメント規約を追加（§12）
- `docs` 安全運用ガイド・実装規約・リファクタリング判断基準・`ai_setup_check_list` — 検証項目を `checklists/` へ移しガイドは原則のみに整理。`Project_map`・`agent_implement`・`05_ディレクトリ構成` を更新
- `docs` `doc/ai_guidelines/安全運用ガイド.md` を新設（ログ・通知・処理量の言語非依存一般原則）
- `docs` Cursor ルールをスリム化: `agent_core.mdc`（常時）・`agent_implement.mdc`（globs）に分割、`agent_workflows.mdc` は後方互換スタブ、Phase 3 詳細は `doc/ai_guidelines/agent_phase3_dod.md` へ移設
- `docs` `doc/reference/` をカテゴリ別サブフォルダ化（`getting-started/` `setup/` `cheatsheets/`）。連番ファイル名を廃止し `README.md` を目次に
- `docs` `doc/specs/` を前プロジェクト由来の内容からテンプレート用に初期化（AI 開発初期リポジトリ運用）

### Added


### Fixed

---

## 記法ガイド

新しいエントリを追加する際は以下の形式に従う。

```
## [vX.Y.Z] — YYYY-MM-DD タイトル

### Added
### Changed
### Fixed
### Removed
### Security

各行末に対応する機能コード（FR-XXX / NFR-XXX）を記載する。
```
