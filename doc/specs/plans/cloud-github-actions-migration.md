# クラウド定期実行 — GitHub Actions 移行 実装計画

最終更新: 2026-09-12
ステータス: **Phase 1 実装済（Secrets 登録と切替は利用者作業）**

手法比較の根拠: [cloud-scheduling-comparison.md](../../reference/setup/cloud-scheduling-comparison.md)
セットアップ手順: [github-actions-hakata-crowding.md](../../reference/setup/github-actions-hakata-crowding.md)

---

## 1. 決定事項

| 項目 | 決定 |
|---|---|
| 実行基盤 | **GitHub Actions**（schedule + workflow_dispatch） |
| リポジトリ | GitHub **公開**（標準 Linux runner は無料） |
| 取得時間帯 | 毎日 **9:00–22:00 JST**（最終取得は 21:30。22:00 ちょうどは `ScheduleGuard` が skip） |
| 実行間隔 | 30 分 |
| keepalive | **毎月 1 日 09:00 JST**（約 30 日周期。ダミー commit なし） |
| 却下 | GAS 全面移植、Render 有料 cron、CF Workers / Vercel 無料枠 |
| ローカル Task Scheduler | 手動実行成功後に **無効化**（削除は任意） |

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
[GitHub Actions crowding  0,30 0-12 * * * UTC（= 9:00–21:30 JST）]
    → uv sync --frozen + uv run python -m hakata_gym_crowding.cli
        → Secrets から .env 相当を注入
        → （同上。ScheduleGuard は変更なし）

[GitHub Actions keepalive  0 0 1 * * UTC（= 毎月1日 09:00 JST）]
    → gh workflow enable（crowding と keepalive）
```

---

## 3. 設計: 認証と Secrets

### 3.1 GitHub Secrets 一覧

| Secret 名 | 内容 | 必須 |
|---|---|---|
| `GOOGLE_SHEETS_CREDENTIALS` | サービスアカウント JSON の **全文** | ○ |
| `SPREADSHEET_ID` | スプレッドシート ID | ○ |
| `SLACK_WEBHOOK_URL` | Incoming Webhook URL | △（通知する場合） |

**任意（既定値で足りる場合は省略可）**:

| Secret 名 | 既定 |
|---|---|
| （workflow 内で固定） | `SHEET_NAME=混雑履歴` / `TIMEZONE=Asia/Tokyo` / `SLACK_NOTIFY_ENABLED=true` |

### 3.2 サービスアカウント（推奨: OAuth ではなく SA）

- 理由: GitHub Actions では **トークン更新** が自動化しづらい。SA JSON は Secrets に置けば期限切れなし
- 手順: 既存 [google-sheets-hakata-crowding.md](../../reference/setup/google-sheets-hakata-crowding.md) の SA を流用
- スプレッドシート共有: SA の `client_email` に編集権限（既存と同じ）

### 3.3 workflow 内での注入

実装正本: [`.github/workflows/hakata_gym_crowding.yml`](../../../.github/workflows/hakata_gym_crowding.yml)

- `printf` で `config/service-account.json` を書く
- `echo` で `config/.env` を書く（HEREDOC のインデント混入を避ける）
- 公開 repo でも Secrets はログに出ないよう、workflow 内で `echo` デバッグしない

---

## 4. 設計: dedup_state（Slack 重複抑制）

### 現状

- ファイル: `logs/.slack_notify_state.json`
- ロジック: `notify/slack.py` の 15 分同一エラー抑制

### 問題（クラウド）

- Actions runner は **毎回クリーン環境** → ローカル JSON は run 間で共有されない
- 同一 ERROR が 30 分ごとに Slack 再送されうる

### 推奨: Sheets `_meta` タブ（未実装・Phase 2）

| 項目 | 内容 |
|---|---|
| タブ名 | `_meta` |
| 列 | `key` / `last_sent_iso` |

ERROR 多発時のみ前倒しする。

---

## 5. cron 設計

### crowding

- `cron: "0,30 0-12 * * *"`（UTC。`timezone` キーは付けない）
- 起動時刻: 9:00, 9:30, …, 21:30 JST（1 日 26 回）。日本時間 = UTC+9（夏時間なし）
- 休館判定は **cron では行わない**（`ScheduleGuard` に委譲）

`timezone: "Asia/Tokyo"` は 2026-09-12 時点で schedule が 0 件だったため採用しない。
旧案の `*/30 * * * *`（UTC 24 時間）も採用しない。時間外起動を減らすため cron 側で開館帯に絞る。

### keepalive

- `cron: "0 0 1 * *"`（UTC = 毎月 1 日 09:00 JST。`timezone` キーは付けない）
- GitHub cron に「ちょうど 30 日」が無いため、月次 1 日を約 30 日周期とする
- `gh workflow enable` で crowding と keepalive を再有効化
- ダミー commit はしない

### 受け入れる制約

- 開始時刻に数分の遅延があり得る（混雑用途では ±10 分を許容）
- 公開 repo は 60 日無活動で schedule が停止する（keepalive で先回り解除）
- schedule の自動実行そのものは「リポジトリ活動」にカウントされない
- `timezone:` キーは使わない。cron は UTC 換算で書く（2026-09-12 の schedule 0 件を踏まえる）

---

## 6. 実装フェーズ

### Phase 0: 準備（利用者作業）

- [ ] GitHub リポジトリに Secrets を登録（§3.1）
- [ ] ローカルで `uv run python -m hakata_gym_crowding.cli --dry-run --force` が成功することを確認

### Phase 1: workflow 追加（実装済）

| ファイル | 役割 |
|---|---|
| `.github/workflows/hakata_gym_crowding.yml` | 混雑取得 |
| `.github/workflows/keepalive.yml` | 60 日停止の先回り解除 |

**切替手順**:

1. `workflow_dispatch` で crowding を **手動 1 回** 実行し、緑と Sheets 追記を確認
2. Windows タスク `HakataGymCrowding` を **無効化**（並行すると行が二重になる）
3. schedule を 1 日観察（9:00 始まり・21:30 終わり）
4. keepalive は手動 `workflow_dispatch` で enable 成功だけ確認

### Phase 2: dedup_state を Sheets 化（未実装）

ERROR 通知が増えたら実施する。

### Phase 3: ドキュメント・運用切替

- [x] README の定期実行正を GitHub Actions に
- [x] windows-scheduled-sync.md をレガシー注記
- [x] 07_CHANGELOG.md に移行記録

---

## 7. 複数スクレイパー向け共通テンプレ（横展開）

HTTP 系 RPA を増やすときの再利用パターン。

```
.github/
  workflows/
    hakata_gym_crowding.yml
    keepalive.yml
```

Selenium 系は VPS + cron を検討する。HTTP 系テンプレは流用しない。

---

## 8. リスクと対策

| リスク | 対策 |
|---|---|
| Secrets 漏洩 | コード・ログに出力しない。SA は最小権限・単一シートのみ |
| Actions 遅延 | ScheduleGuard + 混雑用途で許容 |
| 公式サイトが Actions IP をブロック | 発生時: VPS 固定 IP または手動確認 |
| dedup 未実装のまま移行 | ERROR 通知が増える。Phase 2 を早める |
| schedule 60 日停止 | keepalive（毎月 1 日）で `gh workflow enable` |
| keepalive だけでは足りない | Sheets の行途切れを監視。次手段は空 commit（未実装） |

---

## 9. ロールバック

1. GitHub Actions の crowding workflow を無効化
2. [windows-scheduled-sync.md](../../reference/setup/windows-scheduled-sync.md) に従い Task Scheduler を再有効化
3. ローカル `config/.env` + `service-account.json` は移行中も維持する

---

## 10. 完了定義（Definition of Done）

- [ ] `workflow_dispatch` で crowding が成功し Sheets に行が追加される
- [ ] schedule 実行で 9:00–21:30 JST の行が蓄積される
- [ ] keepalive の手動実行が成功する
- [ ] Windows Task Scheduler が無効化されている
- [ ] 公開 repo のまま Secrets をログに出していない
- [ ] Phase 2 完了時: Slack ERROR 重複抑制が Actions 環境でも機能

---

## 関連

| パス | 内容 |
|---|---|
| [github-actions-hakata-crowding.md](../../reference/setup/github-actions-hakata-crowding.md) | Secrets・切替手順 |
| [cloud-scheduling-comparison.md](../../reference/setup/cloud-scheduling-comparison.md) | 手法比較 |
| [windows-scheduled-sync.md](../../reference/setup/windows-scheduled-sync.md) | レガシー（PC 運用） |
| [README.md](../../../README.md) | プロジェクト入口 |
