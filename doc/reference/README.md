# reference（利用者向けドキュメント）

> **入口はこのファイル**。番号ではなく **カテゴリ + ファイル名** で探す。

`doc/reference/` は仕様（`doc/specs/`）やエージェント規約（`doc/ai/guidelines/`）とは別に、**利用者が読んで作業する手順・早見表** を置く場所です。

---

## カテゴリ一覧

| フォルダ | いつ読むか | ファイル |
|:---|:---|:---|
| [getting-started/](getting-started/) | 初参加・コードの読み方 | [入門ガイド.md](getting-started/入門ガイド.md) / [コード解説.md](getting-started/コード解説.md) / [d-format/](getting-started/d-format/) |
| [setup/](setup/) | スタックを選んで環境構築するとき | [python-uv.md](setup/python-uv.md) / [django.md](setup/django.md) / [gas-clasp-pnpm.md](setup/gas-clasp-pnpm.md) / [gas-operations.md](setup/gas-operations.md) / [product-schema-design.md](setup/product-schema-design.md) / [skills-cli.md](setup/skills-cli.md) / [google-drive-mcp.md](setup/google-drive-mcp.md) |
| [migration/](migration/) | 既存実装の転用・移植 | [meishi-to-product.md](migration/meishi-to-product.md) |
| [cheatsheets/](cheatsheets/) | 作業中に何度も見る | [git.md](cheatsheets/git.md) / [markdown.md](cheatsheets/markdown.md) |
| [learning/](learning/) | テスト・QA など体系的な学習索引 | [ソフトウェアテストとQAの体系.md](learning/ソフトウェアテストとQAの体系.md) |

---

## 目的別クイックリンク

| やりたいこと | 開くファイル |
|:---|:---|
| リポジトリの全体像・フォルダの意味 | [getting-started/入門ガイド.md](getting-started/入門ガイド.md) |
| ソースの読み方・ファイルの役割 | [getting-started/コード解説.md](getting-started/コード解説.md) |
| やりたいこと・コード理解（D形式） | [getting-started/d-format/README.md](getting-started/d-format/README.md) |
| Python / uv の環境構築 | [setup/python-uv.md](setup/python-uv.md) |
| Django のセットアップ・UI 方針 | [setup/django.md](setup/django.md) |
| GAS を clasp + pnpm で開発 | [setup/gas-clasp-pnpm.md](setup/gas-clasp-pnpm.md) |
| 外部 Agent Skills の検索・インストール | [setup/skills-cli.md](setup/skills-cli.md) |
| Google Drive を MCP 経由で参照（個人情報正本） | [setup/google-drive-mcp.md](setup/google-drive-mcp.md) |
| GAS 運用ルール（PoC 参照） | [setup/gas-operations.md](setup/gas-operations.md) |
| 商品DB・重複キー設計 | [setup/product-schema-design.md](setup/product-schema-design.md) |
| 名刺版からの移植 | [migration/meishi-to-product.md](migration/meishi-to-product.md) |
| Git の日常操作 | [cheatsheets/git.md](cheatsheets/git.md) |
| Markdown の書き方 | [cheatsheets/markdown.md](cheatsheets/markdown.md) |
| ソフトウェアテスト・QA の体系（学習索引） | [learning/ソフトウェアテストとQAの体系.md](learning/ソフトウェアテストとQAの体系.md) |

---

## 初めて参加した利用者の読む順（推奨）

1. [getting-started/入門ガイド.md](getting-started/入門ガイド.md)
2. 採用スタックの [setup/](setup/) 手順
3. [cheatsheets/git.md](cheatsheets/git.md)
4. [getting-started/コード解説.md](getting-started/コード解説.md)
5. [getting-started/d-format/README.md](getting-started/d-format/README.md)（処理の流れを D形式で読む）
6. 仕様は [../specs/02_要件定義.md](../specs/02_要件定義.md) / [../specs/04_機能一覧.md](../specs/04_機能一覧.md)

---

## 新しいファイルを追加するとき

1. **連番は付けない**
2. `getting-started/` / `setup/` / `cheatsheets/` / `learning/` のいずれかに入れる
3. **この README.md を更新する**
4. スタック固有の手順は `setup/` に置く（ルートに `pyproject.toml` 等を置かない方針のため）

---

## specs / doc/ai との役割分担

| 置き場所 | 内容 |
|:---|:---|
| `doc/specs/` | 何を作るか・設計・機能 ID・CHANGELOG（**正本**） |
| `doc/ai/sessions/` | 意思決定の経緯・検証（**財産化の正本**） |
| `doc/ai/guidelines/` | エージェント向け規約・既知エラー |
| `doc/reference/`（ここ） | 利用者向けの手順・早見表 |
