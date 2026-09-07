# クラウド定期実行 — GitHub Actions 移行 実装計画

最終更新: 2026-09-07  
ステータス: **計画確定・未実装**

手法比較の根拠: [cloud-scheduling-comparison.md](../../reference/setup/cloud-scheduling-comparison.md)

---

## 1. 決定事項

| 項目 | 決定 |
|---|---|
| 実行基盤 | **GitHub Actions**（schedule + workflow_dispatch） |
| 却下 | GAS 全面移植（Python 完成済みのためコスト大）、Render 有料 cron、CF Workers / Vercel 無料枠 |
| 実行間隔 | 30 分（現行 PC 運用と同等）。cron は UTC、開館外 skip は `ScheduleGuard` に委譲 |
| リポジトリ | GitHub 公開（runner 分無料） |
| ローカル Task Scheduler | 移行完了・動作確認後に **無効化**（削除は任意） |

---

## 2. 現行アーキテクチャ（移行対象）

```
[Windows Task Scheduler]
    → uv run python -m hakata_gym_crowding.cli
        → load_settings (config/.env)
        → ScheduleGuard.evaluate()  … 9-22 JST / 休館 skip
        → PCounterFetcher + TrainingPageFetcher
        → SheetsWriter.append_record()
        → notify_error (Slack, dedup: logs/.slack_notify_state.json)
```

### クラウド移行後

```
[GitHub Actions cron */30 * * * * UTC]
    → uv sync + uv run python -m hakata_gym_crowding.cli
        → Secrets から .env 相当を注入
        → （同上。ScheduleGuard は変更なし）
        → dedup_state は Sheets _meta タブ（Phase 2）
```

---

## 3. 設計: 認証と Secrets

### 3.1 GitHub Secrets 一覧

| Secret 名 | 内容 | 必須 |
|---|---|---|
| `GOOGLE_SHEETS_CREDENTIALS` | サービスアカウント JSON の **全文**（1 行 JSON 文字列） | ○ |
| `SPREADSHEET_ID` | スプレッドシート ID | ○ |
| `SLACK_WEBHOOK_URL` | Incoming Webhook URL | △（通知する場合） |

**任意（既定値で足りる場合は省略可）**:

| Secret 名 | 既定 |
|---|---|
| `SHEET_NAME` | `混雑履歴` |
| `TIMEZONE` | `Asia/Tokyo` |
| `SLACK_NOTIFY_ENABLED` | `true` |

### 3.2 サービスアカウント（推奨: OAuth ではなく SA）

- 理由: GitHub Actions では **トークン更新** が自動化しづらい。SA JSON は Secrets に置けば期限切れなし
- 手順: 既存 [google-sheets-hakata-crowding.md](../../reference/setup/google-sheets-hakata-crowding.md) の SA を流用
- スプレッドシート共有: SA の `client_email` に編集権限（既存と同じ）

### 3.3 workflow 内での注入方法

```yaml
# イメージ（実装時に .github/workflows/ へ配置）
- name: Write credentials file
  run: |
    echo '${{ secrets.GOOGLE_SHEETS_CREDENTIALS }}' > config/service-account.json
  shell: bash

- name: Write env file
  run: |
    cat > config/.env <<EOF
    SPREADSHEET_ID=${{ secrets.SPREADSHEET_ID }}
    GOOGLE_APPLICATION_CREDENTIALS=config/service-account.json
    TIMEZONE=Asia/Tokyo
    SHEET_NAME=混雑履歴
    SLACK_WEBHOOK_URL=${{ secrets.SLACK_WEBHOOK_URL }}
    SLACK_NOTIFY_ENABLED=true
    EOF
```

**注意**: 公開 repo でも Secrets はログに出ないよう、workflow 内で `echo` デバッグしない。

---

## 4. 設計: dedup_state（Slack 重複抑制）

### 現状

- ファイル: `logs/.slack_notify_state.json`（`config.py` が `log_file.parent` 配下に固定）
- ロジック: `notify/slack.py` の `_load_state` / `_save_state`（15 分同一エラー抑制）

### 問題（クラウド）

- Actions runner は **毎回クリーン環境** → ローカル JSON は run 間で共有されない
- 結果: クラウド移行のままだと **同一 ERROR が 30 分ごとに Slack 再送** されうる

### 推奨: Sheets `_meta` タブ

| 項目 | 内容 |
|---|---|
| タブ名 | `_meta`（先頭アンダースコアで履歴タブと区別） |
| 列 | `key` \| `last_sent_iso` |
| key 形式 | 既存 `_dedup_key(stage, detail)` と同じ（`fetch:abc123...`） |

**代替案**:

| 方式 | メリット | デメリット |
|---|---|---|
| Sheets `_meta` タブ | 永続・可視・PC/Cloud 共通 | コード変更（store 層に meta 読書） |
| GitHub Actions Cache | 変更小 | 7 日 TTL・複数 runner で競合しうる |
| 重複抑制を諦める | 変更なし | Slack ノイズ増 |

**実装 Phase**: Phase 2（workflow 単体では Phase 1 から開始可。ERROR 多発時のみ Phase 2 を前倒し）

---

## 5. cron 設計

### 方針

- GitHub Actions: `*/30 * * * *`（UTC、24 時間）
- 開館 9:00–22:00 JST の絞り込みは **cron では行わない**
- `ScheduleGuard` が `outside_hours` / 休館で skip → 現行 Windows「9:00 開始・13 時間・30 分間隔」と **同等の取得タイミング**

### UTC と JST の対応（参考）

| JST | UTC（同日） |
|---|---|
| 9:00 | 0:00 |
| 22:00 | 13:00 |

Actions の遅延（5〜20 分）を許容する。混雑取得用途では **±10 分程度は問題にならない** 想定。

### schedule 無効化の回避

- 60 日非アクティブで schedule 停止 → 月 1 回以上 push または空 commit で維持

---

## 6. 実装フェーズ

### Phase 0: 準備（手動・利用者作業）

- [ ] GitHub リポジトリに Secrets を登録（§3.1）
- [ ] ローカルで `uv run python -m hakata_gym_crowding.cli --dry-run --force` が成功することを確認

### Phase 1: workflow 追加（Pilot）

**成果物**: `.github/workflows/hakata_gym_crowding.yml`

```yaml
name: Hakata Gym Crowding

on:
  workflow_dispatch: {}
  schedule:
    - cron: "*/30 * * * *"

jobs:
  run:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true

      - name: Install dependencies
        run: uv sync --group dev

      - name: Configure secrets
        env:
          GOOGLE_SHEETS_CREDENTIALS: ${{ secrets.GOOGLE_SHEETS_CREDENTIALS }}
          SPREADSHEET_ID: ${{ secrets.SPREADSHEET_ID }}
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: |
          mkdir -p config logs
          printf '%s' "$GOOGLE_SHEETS_CREDENTIALS" > config/service-account.json
          cat > config/.env <<EOF
          SPREADSHEET_ID=${SPREADSHEET_ID}
          GOOGLE_APPLICATION_CREDENTIALS=config/service-account.json
          TIMEZONE=Asia/Tokyo
          SHEET_NAME=混雑履歴
          SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
          SLACK_NOTIFY_ENABLED=true
          EOF

      - name: Run crowding fetch
        run: uv run python -m hakata_gym_crowding.cli

      - name: Upload run log on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: run-log
          path: logs/run.log
          if-no-files-found: ignore
```

**Pilot 手順**:

1. `workflow_dispatch` のみで **手動 1 回** 実行 → 緑確認
2. スプレッドシートに行が追加されたことを確認
3. `schedule` を有効のまま 1 日様子見
4. 問題なければ Windows タスク `HakataGymCrowding` を **無効化**

### Phase 2: dedup_state を Sheets 化（推奨）

**変更ファイル（予定）**:

| ファイル | 変更 |
|---|---|
| `src/hakata_gym_crowding/notify/slack.py` | 状態読書をファイル or Sheets 抽象化 |
| `src/hakata_gym_crowding/store/sheets.py` | `_meta` タブ read/write 追加 |
| `config/.env.example` | `SLACK_DEDUP_BACKEND=file\|sheets`（任意） |
| `tests/test_slack_notify.py` | Sheets backend のモックテスト |

**受け入れ条件**:

- 同一 ERROR を 15 分以内に 2 回 Slack 送信しない（Actions 連続 run でも）

### Phase 3: ドキュメント・運用切替

- [ ] README「セットアップ」に GitHub Actions 節を追加
- [ ] [windows-scheduled-sync.md](../../reference/setup/windows-scheduled-sync.md) 冒頭に「レガシー（PC 運用）」注記
- [ ] `doc/specs/07_CHANGELOG.md` に移行記録

---

## 7. 複数スクレイパー向け共通テンプレ（横展開）

HTTP 系 RPA を増やすときの **再利用パターン**。

### 7.1 構成

```
.github/
  workflows/
    _reusable-python-cron.yml   # workflow_call 正本（将来）
    hakata_gym_crowding.yml     # 本プロジェクト
    youtube_url_fetcher.yml     # 例: 2 本目
```

### 7.2 共通化する要素

| 要素 | 内容 |
|---|---|
| checkout + setup-uv + uv sync | 全 Python RPA 共通 |
| Secrets → config/.env 生成 | プロジェクトごとに Secret 名リストだけ差し替え |
| `uv run python -m {package}.cli` | コマンドのみ差し替え |
| failure 時 artifact | `logs/run.log` |

### 7.3 新規プロジェクト追加手順（チェックリスト）

1. リポジトリ（または monorepo サブディレクトリ）に workflow YAML を 1 ファイル追加
2. GitHub Secrets にそのプロジェクト用 SA / ID / Webhook を登録
3. `workflow_dispatch` で手動成功
4. `schedule` 有効化
5. ローカル Task Scheduler があれば無効化

### 7.4 Selenium 系は別枠

`reportauto_lacicra` 等は **VPS + cron** または Actions + headless Chrome（重い）を検討。HTTP 系テンプレは流用しない。

---

## 8. リスクと対策

| リスク | 対策 |
|---|---|
| Secrets 漏洩 | コード・ログに出力しない。SA は最小権限・単一シートのみ |
| Actions 遅延 | ScheduleGuard + 混雑用途で許容。厳密時刻が必要なら VPS 検討 |
| 公式サイトが Actions IP をブロック | 発生時: VPS 固定 IP または手動確認。現状 HTTP JSON は問題なし想定 |
| dedup 未実装のまま移行 | ERROR 通知が増える。Phase 2 を早めるか `SLACK_NOTIFY_ENABLED=false` で様子見 |
| schedule 60 日停止 | 月 1 push で回避 |

---

## 9. ロールバック

1. GitHub Actions workflow を無効化（YAML 削除 or `schedule` コメントアウト）
2. [windows-scheduled-sync.md](../../reference/setup/windows-scheduled-sync.md) に従い Task Scheduler を再有効化
3. ローカル `config/.env` + `service-account.json` は移行中も維持（並行運用期間可）

---

## 10. 完了定義（Definition of Done）

- [ ] `workflow_dispatch` で 3 回連続成功
- [ ] schedule 実行で Sheets に 9:00–22:00 JST の行が蓄積される
- [ ] `skipped_closed` が時間外 run で記録される（Actions log または Sheets 側で確認）
- [ ] Windows Task Scheduler が無効化されている
- [ ] Phase 2 完了時: Slack ERROR 重複抑制が Actions 環境でも機能

---

## 関連

| パス | 内容 |
|---|---|
| [cloud-scheduling-comparison.md](../../reference/setup/cloud-scheduling-comparison.md) | 手法比較 |
| [windows-scheduled-sync.md](../../reference/setup/windows-scheduled-sync.md) | 現行 PC 運用 |
| [README.md](../../../README.md) | プロジェクト入口 |
