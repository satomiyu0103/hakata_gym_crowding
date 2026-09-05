# Google Drive MCP 運用

> 最終更新: 2026-07-02

[dylancaponi/gdrive-mcp-server](https://github.com/dylancaponi/gdrive-mcp-server) を **drive.readonly** で使い、個人情報の正本を Google Drive に置く手順である。

エージェント向け制約・手順は [gdrive_mcp_core.mdc](../../../.cursor/rules/gdrive_mcp_core.mdc) と [gdrive-mcp/SKILL.md](../../../.cursor/skills/gdrive-mcp/SKILL.md)。背景は [doc/ai/guidelines/google-drive-mcp.md](../../ai/guidelines/google-drive-mcp.md)。

**秘密値（OAuth クライアント ID・トークン等）はリポジトリに置かない。** 設定は `~/.cursor/mcp.json`（グローバル）のみ。

---

## 概要

| 項目 | 内容 |
|---|---|
| **MCP サーバー** | [dylancaponi/gdrive-mcp-server](https://github.com/dylancaponi/gdrive-mcp-server) |
| **既定スコープ** | `drive.readonly`（`GDRIVE_ENABLE_UPLOAD` 未設定） |
| **設定ファイル** | `~/.cursor/mcp.json`（プロジェクトの `.cursor/mcp.json` には書かない） |
| **正本** | Google Drive（例: `Personal/profile.md`） |
| **リポジトリ** | 参照索引のみ |

---

## 前提条件

```powershell
node -v    # v20 以上推奨
npm -v
```

`npm` が「操作可能なプログラムまたはバッチファイルとして認識されていません」と出る場合:

1. **Node.js 未インストール** — [nodejs.org](https://nodejs.org/) から LTS をインストールし、**Cursor を再起動**する
2. **PATH 未反映** — Node インストール直後はターミナルを閉じて開き直す（既存タブは古い PATH のまま）
3. **確認** — 次が通れば OK:

```powershell
node -v
& "C:\Program Files\nodejs\npm.cmd" -v
```

`node` は通るが `npm` だけ失敗するときは、3 のフルパスで `npm.cmd` を使う。

---

## 1. MCP サーバーの clone と build

```powershell
cd $env:USERPROFILE\Documents\dev_tools   # 任意の作業ディレクトリ
git clone https://github.com/dylancaponi/gdrive-mcp-server.git
cd gdrive-mcp-server
npm install
npm run build
```

**Windows で `npm run build` が `chmod` エラーになる場合**（`chmod` は Unix 専用）:

```powershell
npm install --ignore-scripts
npx tsc
```

`dist/index.js` が生成されていれば build 完了。`chmod` は Windows では不要。

clone 先はリポジトリ外に置く（git 管理しない）。

---

## 2. Google Cloud OAuth の準備

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成または選択
2. **Google Drive API** を有効化
3. **OAuth 同意画面** を設定（個人利用は Testing でも可。長期利用は Production 公開を推奨）
4. **認証情報** → **OAuth クライアント ID** → **デスクトップアプリ** を作成
5. JSON をダウンロードし、例: `C:\Users\<USER>\.config\gdrive\gcp-oauth.keys.json` に保存

---

## 3. 初回認証

```powershell
$env:GDRIVE_OAUTH_PATH = "C:\Users\<USER>\.config\gdrive\gcp-oauth.keys.json"
node C:\path\to\gdrive-mcp-server\dist\index.js auth
```

ブラウザで Google アカウントにログインし、権限を許可する。トークンは `~/.gdrive-server-credentials.json`（既定）に保存される。

---

## 4. Cursor MCP 設定

`%USERPROFILE%\.cursor\mcp.json` に追記する（ファイルが無ければ新規作成）。

```json
{
  "mcpServers": {
    "gdrive": {
      "command": "node",
      "args": ["C:/path/to/gdrive-mcp-server/dist/index.js"],
      "env": {
        "GDRIVE_OAUTH_PATH": "C:/Users/<USER>/.config/gdrive/gcp-oauth.keys.json",
        "GDRIVE_CREDENTIALS_PATH": "C:/Users/<USER>/.gdrive-server-credentials.json",
        "GDRIVE_ENABLE_RESOURCES": "false"
      }
    }
  }
}
```

| 環境変数 | 説明 |
|---|---|
| `GDRIVE_OAUTH_PATH` | OAuth クライアント JSON のパス |
| `GDRIVE_CREDENTIALS_PATH` | 保存済みトークンのパス |
| `GDRIVE_ENABLE_RESOURCES` | `false` 推奨（起動時ハング回避） |
| `GDRIVE_ENABLE_UPLOAD` | **設定しない**（readonly 維持） |
| `GDRIVE_ENABLE_SHEETS` | 未設定（Sheets 範囲読取が必要なときのみ `true` + 再 `auth`） |

パスは **スラッシュ `/` またはエスケープしたバックスラッシュ** を使う。`<USER>` と `C:/path/to/` は実環境に置き換える。

**Cursor を再起動** して MCP 接続を反映する。

---

## 5. 接続確認

Cursor のチャットで次を試す。

```text
Google Drive で「profile」を検索して、ファイル一覧を教えて
```

`search` が動けば設定は成功している。

---

## 6. Drive 側のフォルダ構成（推奨）

```text
Google Drive/Personal/
└── profile.md   # または Google ドキュメント
```

リポジトリの `memory_stream` には次の粒度のみ追記する。

```markdown
- 正本: Google Drive > Personal > profile.md
- 検索キーワード: profile
```

---

## やってはいけないこと

- OAuth 鍵・トークン・`mcp.json` をプロジェクトリポジトリに commit する
- プロジェクトの `.cursor/mcp.json` に個人用 Drive 設定を書く
- エージェントに Drive から取得した個人情報本文を doc に保存させる

---

## 書き込みが必要になったとき

readonly からの昇格は利用者が明示したときのみ。

1. `GDRIVE_ENABLE_UPLOAD=true` を `mcp.json` の `env` に追加
2. `node dist/index.js auth` で再認証
3. [gdrive-mcp/SKILL.md](../../../.cursor/skills/gdrive-mcp/SKILL.md) §スコープ昇格に従い Rule / 意思決定を更新

---

## 公式リモート MCP への移行

Google 公式（`https://drivemcp.googleapis.com/mcp/v1`）が GA で機能拡充した場合、[gdrive-mcp/SKILL.md](../../../.cursor/skills/gdrive-mcp/SKILL.md) §移行検討トリガに従い再検討する。

---

## トラブルシューティング

| 症状 | 対処 |
|---|---|
| `npm` が認識されない | Node.js インストール後に Cursor 再起動。`& "C:\Program Files\nodejs\npm.cmd" -v` で確認 |
| `chmod` が認識されない（build 失敗） | `npm install --ignore-scripts` のあと `npx tsc` |
| MCP が Cursor に表示されない | Cursor 再起動。`mcp.json` の JSON 構文・パスを確認 |
| 認証が切れた | `node dist/index.js auth` を再実行。OAuth が Testing なら 7 日期限を確認 |
| 起動が固まる | `GDRIVE_ENABLE_RESOURCES=false` を確認 |
| 既存ファイルが読めない | readonly スコープで `auth` 済みか確認。Drive 上の共有権限を確認 |
| Windows でパスエラー | 絶対パスを使用。`C:/Users/...` 形式を推奨 |

再現性のある障害は `doc/ai/guidelines/試験実装のエラー.md` への昇格を検討する。

---

## 参考リンク

- [dylancaponi/gdrive-mcp-server README](https://github.com/dylancaponi/gdrive-mcp-server)
- [Google Drive MCP 公式（リモート）](https://developers.google.com/workspace/drive/api/guides/configure-mcp-server)
- [Cursor MCP ドキュメント](https://cursor.com/docs/mcp)
- [skills-cli.md](skills-cli.md) — Skills と MCP の使い分け
- [doc/ai/guidelines/google-drive-mcp.md](../../ai/guidelines/google-drive-mcp.md) — 背景・採用理由
