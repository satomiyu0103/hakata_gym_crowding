# Windows タスクスケジューラ設定（博多体育館混雑 RPA）

最終更新: 2026-09-10

> **クラウド移行検討中**: PC 常時起動を避ける場合は [cloud-scheduling-comparison.md](cloud-scheduling-comparison.md)（手法比較）と [cloud-github-actions-migration.md](../../specs/plans/cloud-github-actions-migration.md)（実装計画）を参照。移行完了後は本 doc はロールバック用として残す。

30 分間隔で 9:00〜22:00 の開館時間帯に混雑データを取得する手順です。休館判定は CLI 側（`ScheduleGuard`）が行うため、スケジューラは **時間帯内で定期起動** すれば足ります。

---

## 定期実行の前提（重要）

**毎日 9:00 の初回トリガー時点で、PC が起動しており、かつユーザーがログオンしている必要がある**（タスクが「ログオン時のみ」の場合）。

| 条件 | 初回 9:00 を逃したとき |
|---|---|
| PC スリープ中 | 当日の 30 分繰り返し（計 26 回）が **まとめて見逃し** になり、ログオン後も自動再開しないことがある |
| ログオン前 | Interactive タスクは実行されない |
| 手動実行のみ成功 | RPA 本体は正常。スケジューラ側の取りこぼしを疑う |

`StartWhenAvailable`（起動後に実行）と `WakeToRun`（スリープ解除）は ON でも、**初回を逃した日の残り 25 回を自動補完しない**。

---

## 前提

- [google-sheets-hakata-crowding.md](google-sheets-hakata-crowding.md) の初回セットアップ完了
- `uv sync` 済み
- リポジトリパス例: `D:\pc_handover_2026-07\Documents\Development\RPA_scripts\hakata_gym_crowding`

---

## 実行コマンド

```powershell
uv run python -m hakata_gym_crowding.cli
```

またはエントリポイント:

```powershell
uv run hakata-crowding
```

---

## GUI での登録（推奨）

1. **タスクスケジューラ** を開く
2. **基本タスクの作成**
3. 名前: `HakataGymCrowding`
4. トリガー: **毎日**、開始 `9:00:00`
5. 操作: **プログラムの開始**
   - プログラム: `C:\Users\{ユーザー}\.local\bin\uv.exe`（`where uv` で確認）
   - 引数: `run python -m hakata_gym_crowding.cli`
   - 開始: リポジトリルート（`hakata_gym_crowding`）
6. タスクの **プロパティ** → **トリガー** → 詳細設定
   - **間隔**: 30 分
   - **継続時間**: 13 時間（9:00 開始なら 22:00 まで）
7. **条件** タブ: 「コンピューターを AC 電源で使用している場合のみ」等は環境に合わせて調整

---

## PowerShell 登録例（上級）

`uv` のフルパスを `$uvPath` に置き換えて実行します。

```powershell
$repo = "D:\pc_handover_2026-07\Documents\Development\RPA_scripts\hakata_gym_crowding"
$uvPath = (Get-Command uv).Source

$action = New-ScheduledTaskAction `
  -Execute $uvPath `
  -Argument "run python -m hakata_gym_crowding.cli" `
  -WorkingDirectory $repo

$trigger = New-ScheduledTaskTrigger `
  -Daily `
  -At "09:00" `
  -RepetitionInterval (New-TimeSpan -Minutes 30) `
  -RepetitionDuration (New-TimeSpan -Hours 13)

Register-ScheduledTask `
  -TaskName "HakataGymCrowding" `
  -Action $action `
  -Trigger $trigger `
  -Description "博多体育館混雑取得 RPA（30分間隔・9-22時）"
```

---

## ログ確認

| 種別 | パス |
|---|---|
| 実行ログ | `logs/run.log` |
| Slack 重複抑制状態 | `logs/.slack_notify_state.json` |
| データ | Google スプレッドシート「混雑履歴」 |

`skipped_closed` は休館・時間外で正常スキップです。

ERROR 時の Slack 通知設定: [slack-webhook-hakata-crowding.md](slack-webhook-hakata-crowding.md)

### 定期実行が止まったとき（トラブルシュート）

1. **タスクの見逃し数** — `Get-ScheduledTaskInfo -TaskName HakataGymCrowding` で `NumberOfMissedRuns` を確認。20 前後なら当日の初回トリガー逃し
2. **run.log の時刻** — 当日エントリが `:34` など **:00/:30 以外** だけ → 手動 BAT 実行の可能性大
3. **スリープ履歴** — 当日 9:00 前にスリープしていたか（イベントログの復帰時刻）
4. **RPA 単体** — `Start-ScheduledTask -TaskName HakataGymCrowding` または `--dry-run --force` で成功するか

対処案の詳細・ログオン時救済タスクの登録例: [試験実装のエラー.md](../../ai/guidelines/試験実装のエラー.md)（2026-09-10 項）

---

## 手動テスト

```powershell
# 取得のみ
uv run python -m hakata_gym_crowding.cli --dry-run --force

# 休館判定を無視して Sheets 書込（設定済みの場合）
uv run python -m hakata_gym_crowding.cli --force
```

---

## リポジトリ移動後（必須）

リポジトリのパスを変えたとき、デスクトップショートカットだけ更新しても **定期実行は止まったまま** になる。次を **セット** で行う。

1. ショートカット再作成（[手動実行（デスクトップ・パターン A）](#手動実行デスクトップパターン-a) の `create_desktop_shortcuts.ps1`）
2. タスク `HakataGymCrowding` の **開始（作業フォルダ）** を新しいリポジトリルートに変更（[PowerShell 登録例](#powershell-登録例上級) の `$repo` を現パスに合わせて `Set-ScheduledTask`）
3. `uv run python -m hakata_gym_crowding.cli --dry-run --force` で `logs/run.log` を確認

症状・エラーコード `0x8007010B`: [試験実装のエラー.md](../../ai/guidelines/試験実装のエラー.md)（2026-09-06 項）

---

## 手動実行（デスクトップ・パターン A）

BAT の **正本はリポジトリ内**、デスクトップには **ショートカットのみ** 置く運用です。BAT を更新するとショートカット経由でも即反映されます。

| 種別 | パス |
|---|---|
| 通常実行 BAT（正本） | `scripts/run_hakata_crowding.bat` |
| テスト用 BAT（正本） | `scripts/run_hakata_crowding_dry_run.bat`（`--dry-run --force`） |
| ショートカット作成 | `scripts/create_desktop_shortcuts.ps1` |
| デスクトップ配置先 | `%USERPROFILE%\Desktop\RPA\` |

### 初回・PC 移行後

リポジトリルートで次を実行します。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\create_desktop_shortcuts.ps1
```

作成されるショートカット:

| ショートカット名 | 内容 |
|---|---|
| `博多体育館混雑取得.lnk` | 通常実行（開館判定あり・Sheets 追記） |
| `博多体育館混雑取得_テスト.lnk` | dry-run（取得のみ・休館判定スキップ） |

ダブルクリック後、黒い画面（コマンドプロンプト）に結果が表示され、キー入力で閉じます。エラー時は `logs/run.log` を確認してください。

---

## 関連

- Sheets セットアップ: [google-sheets-hakata-crowding.md](google-sheets-hakata-crowding.md)
- 休館ロジック: [doc/specs/03_システム設計.md](../../specs/03_システム設計.md)
