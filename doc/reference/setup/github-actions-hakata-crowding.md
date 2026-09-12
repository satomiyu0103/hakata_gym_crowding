# GitHub Actions 定期実行（博多体育館混雑 RPA）

最終更新: 2026-09-12

公開リポジトリのまま、GitHub 上の仮想マシン（runner）で混雑取得を定期実行する手順です。
PC を起動したままにする必要はありません。

設計の根拠は [cloud-github-actions-migration.md](../../specs/plans/cloud-github-actions-migration.md) です。
手法比較は [cloud-scheduling-comparison.md](cloud-scheduling-comparison.md) です。

---

## 何が動くか

| workflow | ファイル | いつ |
|---|---|---|
| 混雑取得 | `.github/workflows/hakata_gym_crowding.yml` | 毎日 9:00–21:30 JST、30 分間隔 |
| keepalive | `.github/workflows/keepalive.yml` | 毎月 1 日 09:00 JST |

22:00 ちょうどはプログラム側（`ScheduleGuard`）が取得対象外です。
休館日も同じ判定でスキップします。

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

## 5. 定期実行を 1 日観察する

翌日以降、Actions の crowding が 9:00 前後に始まり、21:30 前後で終わることを確認します。
GitHub 側の開始は数分遅れることがあります。混雑取得では問題にしません。

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
