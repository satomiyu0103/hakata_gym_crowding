# GAS 開発環境構築ガイド（Node.js + pnpm + clasp）

> 最終更新: {{LAST_UPDATED}}

Google Apps Script（GAS）を **ローカルで編集し、clasp で push/pull する**ための手順です。
主に Windows（PowerShell）向けに記載し、補足で Unix/macOS 向けコマンドも示します。

## 概要


| ツール         | 役割                                 |
| ----------- | ---------------------------------- |
| **Node.js** | clasp・ビルドツール・型チェックの実行基盤            |
| **pnpm**    | 依存関係と npm スクリプトの管理                 |
| **clasp**   | ローカル ↔ Google ドライブ上の GAS プロジェクトの同期 |


エディタは Cursor / VS Code を想定します。GAS 本体はクラウド上にあり、ローカルは「作業コピー」です。

---

## 前提条件

- Google アカウント（GAS を実行するアカウント）
- 初回のみ [Google Apps Script API](https://script.google.com/home/usersettings) を **オン**
- インターネット接続（`clasp login` でブラウザ認証）

---

## 1. Node.js のインストール

[LTS 版](https://nodejs.org/) をインストールする。

```powershell
node -v
npm -v
```

`v20` 以上（または最新 LTS）が無難です。

---

## 2. pnpm の有効化

Node 18.12+ では Corepack で pnpm を有効化できる。

```powershell
corepack enable
corepack prepare pnpm@latest --activate
pnpm -v
```

Corepack が使えない場合:

```powershell
npm install -g pnpm
```

---

## 3. 新規 GAS プロジェクトを作る（ローカル起点）

作業用ディレクトリを作成し、初期化する。

```powershell
mkdir my-gas-project
Set-Location my-gas-project
pnpm init
```

clasp と型定義を開発依存として入れる。

```powershell
pnpm add -D @google/clasp @types/google-apps-script typescript
```

`package.json` にスクリプトを追加する（後述の例をコピー）。

Google 側に新規スクリプトを作り、ローカルと紐付ける。

```powershell
pnpm exec clasp login
pnpm exec clasp create --type standalone --title "My GAS Project" --rootDir ./src
```

`--type` の例:


| 値            | 用途          |
| ------------ | ----------- |
| `standalone` | 単体スクリプト     |
| `sheets`     | スプレッドシート紐付け |
| `docs`       | ドキュメント紐付け   |
| `forms`      | フォーム紐付け     |


作成後、ルートに `.clasp.json` と `src/`（`appsscript.json` 等）ができる。

---

## 4. 既存 GAS を clone する（クラウド起点）

スクリプト ID はエディタの **プロジェクトの設定 → スクリプト ID** から取得する。

```powershell
mkdir my-gas-project
Set-Location my-gas-project
pnpm init
pnpm add -D @google/clasp @types/google-apps-script typescript

pnpm exec clasp login
pnpm exec clasp clone <SCRIPT_ID>
```

`clone` 後は `.clasp.json` が生成される。`rootDir` が意図と違う場合は `.clasp.json` を編集する。

---

## 5. 推奨ディレクトリ構成

```
my-gas-project/
├── .clasp.json           # clasp 設定（scriptId, rootDir 等）
├── .gitignore
├── package.json
├── pnpm-lock.yaml
├── tsconfig.json         # TypeScript 利用時（任意）
└── src/                  # push 対象（rootDir と一致させる）
    ├── appsscript.json   # マニフェスト
    ├── Code.ts           # または .js
    └── ...
```

`.clasp.json` の例:

```json
{
  "scriptId": "<スクリプトID>",
  "rootDir": "./src"
}
```

**秘密情報**（API キー、トークン）は `PropertiesService` や clasp の `.claspignore` で管理し、リポジトリに直書きしない。

---

## 6. package.json のスクリプト例

```json
{
  "name": "my-gas-project",
  "private": true,
  "scripts": {
    "login": "clasp login",
    "pull": "clasp pull",
    "push": "clasp push",
    "open": "clasp open",
    "deploy": "clasp deploy",
    "logs": "clasp logs --watch"
  },
  "devDependencies": {
    "@google/clasp": "^2.4.2",
    "@types/google-apps-script": "^1.0.83",
    "typescript": "^5.0.0"
  }
}
```

日常の操作:

```powershell
pnpm pull          # クラウド → ローカル
pnpm push          # ローカル → クラウド
pnpm open          # ブラウザでスクリプトエディタを開く
```

TypeScript をそのまま push する場合は、プロジェクト方針に合わせてビルド（`tsc` や `esbuild`）してから `src/` に `.js` を出力する構成も多い。初めは `**.gs` / `.js` のみで push** から始めてよい。

---

## 7. .gitignore

このテンプレートのルート `[.gitignore](../../.gitignore)` に `node_modules/` と `.clasprc.json` を含めています。

`.clasprc.json` には認証情報が含まれるため **Git に含めない**。`.clasp.json`（scriptId）はコミットしてよい。

---

## 8. よく使う clasp コマンド


| やりたいこと      | コマンド                           |
| ----------- | ------------------------------ |
| ログイン        | `pnpm exec clasp login`        |
| ログアウト       | `pnpm exec clasp logout`       |
| 状態確認        | `pnpm exec clasp list`         |
| 取り込み        | `pnpm exec clasp pull`         |
| 反映          | `pnpm exec clasp push`         |
| 強制反映（上書き注意） | `pnpm exec clasp push --force` |
| エディタを開く     | `pnpm exec clasp open`         |
| デプロイ一覧      | `pnpm exec clasp deployments`  |
| 実行ログ        | `pnpm exec clasp logs`         |


---

## 9. トラブルシューティング

### `User has not enabled the Apps Script API`

[ユーザー設定](https://script.google.com/home/usersettings) で **Google Apps Script API** をオンにする。

### `Insufficient Permission` / 認証エラー

```powershell
pnpm exec clasp logout
pnpm exec clasp login
```

別 Google アカウントで作ったプロジェクトに、別アカウントで push していないか確認する。

### `Project settings not found` / scriptId が無効

`.clasp.json` の `scriptId` をエディタの設定と照合する。`clasp clone` をやり直す。

### push しても反映されない

- `rootDir` と実際のソース配置が一致しているか
- `.claspignore` でファイルが除外されていないか
- エディタ側で手動変更があり、`pull` で上書きされていないか

### `pnpm` が見つからない

```powershell
corepack enable
corepack prepare pnpm@latest --activate
```

---

## 10. このテンプレートリポジトリとの関係

`ai-agent-devenv-template` は **Python / uv** 向けの雛形です。GAS プロジェクトは通常 **別リポジトリ**（または別ディレクトリ）で上記手順を行います。


| 領域        | 参照先                                                          |
| --------- | ------------------------------------------------------------ |
| Python 環境 | [python-uv.md](python-uv.md) |
| Git 操作    | [../cheatsheets/git.md](../cheatsheets/git.md) |
| reference 目次 | [../README.md](../README.md) |
| エラー記録     | [../ai/guidelines/試験実装のエラー.md](../ai/guidelines/試験実装のエラー.md) |


---

## まとめ（PowerShell）

```powershell
# 新規
mkdir my-gas-project; Set-Location my-gas-project
corepack enable
pnpm init
pnpm add -D @google/clasp @types/google-apps-script typescript
pnpm exec clasp login
pnpm exec clasp create --type standalone --title "My GAS Project" --rootDir ./src

# 日常
pnpm pull
# 編集 …
pnpm push
pnpm open
```

---

## 参考リンク

- [clasp（GitHub）](https://github.com/google/clasp)
- [Apps Script 公式ドキュメント](https://developers.google.com/apps-script)

