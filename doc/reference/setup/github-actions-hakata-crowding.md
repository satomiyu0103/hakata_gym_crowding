# GitHub Actions 定期実行（博多体育館混雑 RPA）

最終更新: 2026-09-12

公開リポジトリのまま、GitHub 上の仮想マシン（runner）で混雑取得を定期実行する手順です。
PC を起動したままにする必要はありません。

設計の根拠は [cloud-github-actions-migration.md](../../specs/plans/cloud-github-actions-migration.md) です。
手法比較は [cloud-scheduling-comparison.md](cloud-scheduling-comparison.md) です。

---

## 何が動くか

| workflow | ファイル | いつ（日本時間） | cron（UTC） |
|---|---|---|---|
| 混雑取得 | `.github/workflows/hakata_gym_crowding.yml` | 毎日 9:00–21:30、30 分間隔 | `0,30 0-12 * * *` |
| keepalive | `.github/workflows/keepalive.yml` | 毎月 1 日 09:00 | `0 0 1 * *` |

22:00 ちょうどはプログラム側（`ScheduleGuard`）が取得対象外です。
休館日も同じ判定でスキップします。

**cron**：分・時・日・月・曜日の 5 つで起動時刻を書く式です。
GitHub の schedule は **UTC**（世界の基準時。日本時間より 9 時間遅れ）で解釈します。
日本時間の開館帯は UTC に換算して書きます。
`timezone:` キーは付けません（2026-09-12 に `Asia/Tokyo` 付きでは schedule が 0 件だったため）。

日本には夏時間がないので、UTC+9 の換算は通年で同じです。

**GitHub Actions**：GitHub が用意するクラウド上の実行環境です。PC の代わりに Python を動かします。

**Secrets**：API 鍵などをコードに書かず GitHub 側に置く保管庫です。公開リポジトリでも値は見えません。

---

## 前提

- リポジトリが GitHub の **公開** リポジトリである
- [google-sheets-hakata-crowding.md](google-sheets-hakata-crowding.md) のサービスアカウントで、スプレッドシートへ書き込める
- ローカルで次が成功する

```powershell
uv run python -m hakata_gym_crowding.cli --dry-run --force
```

---

## 1. Secrets を登録する

GitHub のリポジトリページで **Settings → Secrets and variables → Actions → New repository secret** を開きます。

| 名前 | 値 |
|---|---|
| `GOOGLE_SHEETS_CREDENTIALS` | `config/service-account.json` の **全文**（1 ファイルをそのまま貼る） |
| `SPREADSHEET_ID` | `config/.env` の `SPREADSHEET_ID` と同じ |
| `SLACK_WEBHOOK_URL` | 通知する場合のみ。`config/.env` と同じ |

JSON を 1 行に圧縮する必要はありません。
workflow は受け取った文字列をそのままファイルに書きます。

登録した値をチャットや issue に貼らないでください。

---

## 2. ブランチを default に載せる

schedule（定期実行）は **default ブランチ**（通常 `master`）の workflow だけが動きます。
`feat/github-actions-migration` 上にあるうちは、手動実行もそのブランチ向けです。
定期実行を始める前に、default ブランチへマージしてください。

---

## 3. 手動で 1 回試す（開館時間内）

1. GitHub の **Actions** タブを開く
2. 左の **Hakata Gym Crowding** を選ぶ
3. **Run workflow** を実行する
4. 緑（成功）を確認する
5. スプレッドシート「混雑履歴」に 1 行増えたことを確認する

失敗したときは、同じ run の artifact `run-log`（あれば）とステップログを見ます。
ログに JSON 全文や Webhook URL が出ていないことも確認します。

---

## 4. Windows タスクを無効化する

手動実行が成功したら、PC 側の定期実行を止めます。
両方動かすと、同じ時刻付近で **行が二重** になります。

```powershell
Disable-ScheduledTask -TaskName "HakataGymCrowding"
```

無効化の確認:

```powershell
Get-ScheduledTask -TaskName "HakataGymCrowding" | Select-Object TaskName, State
```

`State` が `Disabled` であれば停止です。
タスクの削除は任意です。ロールバック用に残してかまいません。

手動用のデスクトップショートカットはそのまま使えます。

---

## 5. 定期実行を確認する（schedule）

**schedule**：GitHub が決まった時刻にワークフローを自動で起こす仕組みです。
Actions 画面の「Run workflow」による手動実行（**workflow_dispatch**）とは別です。
手動が成功しても、schedule が動いていることにはなりません。

### マージ直後（次の UTC 0 分または 30 分）

default ブランチへマージしたあと、次の UTC 0 分または 30 分を待ちます。
開館帯なら、それは日本時間の 9:00–21:30 の枠に対応します。
GitHub 側の開始は数分遅れることがあります。混雑取得では問題にしません。

確認手順:

1. GitHub の **Actions** タブを開く
2. 左の **Hakata Gym Crowding** を選ぶ
3. 一覧の Event 列が `schedule` の run があることを確認する（`workflow_dispatch` だけなら未発火）
4. 緑（成功）なら、スプレッドシート「混雑履歴」に行が増えたことも確認する
5. 実験用 workflow「Hakata Gym Crowding UTC Experiment」が一覧から消えていることを確認する

API で件数を見る場合:

```powershell
gh api "repos/satomiyu0103/hakata_gym_crowding/actions/runs?event=schedule&per_page=5"
gh run list --workflow=hakata_gym_crowding.yml --limit 10
```

`event=schedule` が 1 件以上あれば初回成功です。
30 分以上待っても 0 件なら、workflow の Disable のあと Enable、keepalive の手動実行を試します。

### 1 日観察

翌日以降、Actions の crowding が 9:00 前後（日本時間）に始まり、21:30 前後で終わることを確認します。

---

## 6. keepalive を手動確認する

毎月 1 日を待たず、Actions で **Keepalive scheduled workflows** を **Run workflow** します。
緑なら、`gh workflow enable` が crowding と keepalive の両方に通っています。

### 60 日ルール

公開リポジトリでは、**60 日間リポジトリ活動（push など）が無い** と schedule が自動停止します。
定期実行そのものは活動に数えられません。

keepalive はダミー commit をせず、enable API で停止を先回り解除します。
それでも止まったときは、Actions 画面の **Enable workflow** を押します。

開館日なのに Sheets の行が増えない場合は、停止を疑ってください。

---

## ロールバック（PC 運用に戻す）

1. Actions の **Hakata Gym Crowding** を Disable workflow する
2. [windows-scheduled-sync.md](windows-scheduled-sync.md) に従い `HakataGymCrowding` を再有効化する

```powershell
Enable-ScheduledTask -TaskName "HakataGymCrowding"
```

ローカルの `config/.env` と `config/service-account.json` は残しておきます。

---

## 関連

| ドキュメント | 内容 |
|---|---|
| [cloud-github-actions-migration.md](../../specs/plans/cloud-github-actions-migration.md) | 実装計画 |
| [windows-scheduled-sync.md](windows-scheduled-sync.md) | レガシー（PC 運用） |
| [google-sheets-hakata-crowding.md](google-sheets-hakata-crowding.md) | Sheets とサービスアカウント |
| [slack-webhook-hakata-crowding.md](slack-webhook-hakata-crowding.md) | Slack 通知 |
