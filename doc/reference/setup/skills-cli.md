# Agent Skills CLI 利用ガイド（vercel-labs/skills）

> 最終更新: 2026-07-02

[vercel-labs/skills](https://github.com/vercel-labs/skills) は、コミュニティ公開の **Agent Skills** を検索・インストール・管理する CLI です。  
`npx skills` でその場実行でき、**別途グローバルインストールは不要**です。

本テンプレの `.cursor/skills/`（Phase 1〜3・監査等の**プロジェクト手順**）とは別物です。外部スキルを足したいときに使います。

---

## 概要

| 項目 | 内容 |
|---|---|
| **CLI** | `npx skills`（npm パッケージ `skills`） |
| **前提** | Node.js（LTS 推奨。`node -v` で確認） |
| **スキル一覧サイト** | [skills.sh](https://skills.sh/) |
| **公式リポジトリ** | [github.com/vercel-labs/skills](https://github.com/vercel-labs/skills) |

### 3 種類の Skills の違い

| 種類 | 置き場所 | 役割 |
|---|---|---|
| **本テンプレ同梱** | `.cursor/skills/` | Phase 1〜3・監査・CHANGELOG 等の**プロジェクト運用手順**（clone 時に同梱） |
| **Cursor 標準** | `~/.cursor/skills-cursor/` | Cursor IDE 同梱（`create-skill`, `review-bugbot` 等）。編集不要 |
| **外部スキル（CLI）** | `~/.agents/skills/`（グローバル）または `.agents/skills/`（プロジェクト） | [skills.sh](https://skills.sh/) 等から `npx skills add` で追加 |

実行層の全体像は [doc/ai/runtime.md](../../ai/runtime.md) を参照。

---

## 前提条件

```powershell
node -v    # v20 以上推奨
npm -v
npx skills --help
```

初回は `npx` が `skills` パッケージを自動取得します。

---

## 初回セットアップ（推奨: find-skills）

「使える Skill が分からない」ときの出発点として **find-skills** を入れておくと便利です。

```powershell
npx skills add https://github.com/vercel-labs/skills --skill find-skills -g -a cursor -y
```

| オプション | 意味 |
|---|---|
| `-g` | グローバル（全プロジェクトで利用） |
| `-a cursor` | Cursor 向けにインストール |
| `-y` | 確認プロンプトをスキップ |
| `--skill find-skills` | リポジトリ内の特定スキルのみ |

インストール後、**Cursor を再起動**するとエージェントが読み込みます。

---

## よく使うコマンド

### スキルを検索する

```powershell
# キーワード検索
npx skills find typescript
npx skills find pdf

# 特定オーナー内を検索
npx skills find react --owner vercel

# 対話式検索
npx skills find
```

### スキルをインストールする

```powershell
# リポジトリ内のスキル一覧を確認（インストールしない）
npx skills add vercel-labs/agent-skills --list

# 特定スキルを Cursor にグローバルインストール
npx skills add vercel-labs/agent-skills --skill frontend-design -g -a cursor -y

# 本プロジェクトのみにインストール（カレントディレクトリで実行）
npx skills add vercel-labs/agent-skills --skill frontend-design -a cursor -y
```

### インストール済みを確認・更新・削除

```powershell
# 一覧（グローバル）
npx skills ls -g

# Cursor 向けのみ
npx skills ls -g -a cursor

# 更新
npx skills update -g -y

# 削除
npx skills remove find-skills -g -y
```

### 自作スキルを作る

```powershell
npx skills init my-skill
# → my-skill/SKILL.md が生成される
```

### インストールせず一時利用

```powershell
npx skills use vercel-labs/agent-skills --skill web-design-guidelines
```

---

## Cursor での使い方

Skills はスラッシュコマンドではありません。チャットで自然に話しかけると、エージェントが該当 Skill を読み込みます。

**聞き方の例:**

- 「PDF を整理する Skill を探してください」
- 「コードレビューに使える Skill はありますか？」
- 「README 作成に使える Skill を探して」
- 「〇〇 というスキルをインストールしてください」

`find-skills` が入っている場合、上記のような依頼で候補を検索し、インストールコマンドを提案してくれます。

---

## スコープの選び方

| スコープ | フラグ | インストール先（Cursor） | 用途 |
|---|---|---|---|
| **プロジェクト** | （省略） | `.agents/skills/` | チームで共有したいスキル。リポジトリにコミットする運用ならこちら |
| **グローバル** | `-g` | `~/.agents/skills/` | 個人の全プロジェクトで使うスキル（find-skills 等） |

本テンプレの **運用手順**（Phase 1〜3 等）は `.cursor/skills/` にあり、Skills CLI とは別管理です。混同しないこと。

---

## スキルを選ぶときの基準

候補が複数あるときは、すぐに入れず確認します。

1. **インストール数** … 目安として 1,000 以上。広く使われているほど内容が検証されている可能性が高い
2. **提供元** … Vercel Labs・Anthropic 等の公式・有名リポジトリを優先。個人リポジトリは README・更新状況を確認
3. **中身** … 何をするスキルか、外部接続やコマンド実行を含むか、機密データを扱ってよいか

研究データ・未公開原稿を扱う場合は、インストール数だけで判断しないこと。

---

## Skills と MCP の使い分け

| やりたいこと | 向いている仕組み |
|---|---|
| PubMed・Semantic Scholar・Zotero 等の**外部 DB に接続**する | **MCP** |
| 論文 PDF の要約形式・査読前チェックリスト等の**作業手順を固定**する | **Skills** |
| 文献を探す | MCP |
| 読んだ文献を決まった形式で整理する | Skills |

外部データを探すなら MCP、手順を再利用するなら Skills、と分けて考えると迷いにくい。

個人情報の正本を Google Drive に置き MCP で参照する運用は [google-drive-mcp.md](google-drive-mcp.md) を参照。

---

## ソース形式（add の引数）

```powershell
# GitHub 省略形
npx skills add vercel-labs/agent-skills

# フル URL
npx skills add https://github.com/vercel-labs/agent-skills

# リポジトリ内の特定パス
npx skills add https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines

# ローカルパス
npx skills add ./my-local-skills
```

---

## トラブルシューティング

| 症状 | 対処 |
|---|---|
| `npx skills` が動かない | Node.js をインストール・PATH を確認 |
| スキルがエージェントに反映されない | Cursor を再起動。`npx skills ls -g -a cursor` でパスを確認 |
| `No skills found` | リポジトリに有効な `SKILL.md`（`name`・`description` の frontmatter）があるか確認 |
| 権限エラー | インストール先ディレクトリへの書き込み権限を確認 |

---

## 参考リンク

- [vercel-labs/skills README](https://github.com/vercel-labs/skills)
- [skills.sh — スキルディレクトリ](https://skills.sh/)
- [欲しい Skills が判らないときに使う find-skills（Ozk / note）](https://note.com/ozk7311/n/nc165c8301e2b)
- 本テンプレの実行層説明: [doc/ai/runtime.md](../../ai/runtime.md)
- 本テンプレ同梱 Skills 一覧: [doc/ai/guidelines/Project_map.md](../../ai/guidelines/Project_map.md)
