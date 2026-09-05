# Google スプレッドシート初回セットアップ（博多体育館混雑 RPA）

最終更新: 2026-09-05

博多体育館混雑取得 RPA が Google スプレッドシートへ書き込むための初回手順です。

---

## 前提

- Google アカウント（個人 Gmail 可）
- 本リポジトリで `uv sync` 済み
- 秘密ファイル（`.env`・サービスアカウント JSON）は **Git にコミットしない**

---

## 1. Google Cloud プロジェクト

1. [Google Cloud Console](https://console.cloud.google.com/) を開く
2. 新規プロジェクトを作成（例: `hakata-gym-crowding`）

---

## 2. Google Sheets API を有効化

1. Cloud Console → **API とサービス** → **ライブラリ**
2. **Google Sheets API** を検索して **有効化**

---

## 3. サービスアカウントと JSON 鍵

1. **API とサービス** → **認証情報** → **認証情報を作成** → **サービスアカウント**
2. 名前は任意（例: `hakata-crowding-writer`）
3. 作成後、サービスアカウントを開き **キー** タブ → **鍵を追加** → **JSON**
4. ダウンロードした JSON を次のパスに保存:

```text
config/service-account.json
```

5. JSON 内の `client_email`（例: `...@....iam.gserviceaccount.com`）を控える

---

## 4. スプレッドシート作成と共有

1. Google スプレッドシートを新規作成
2. シート名を **混雑履歴** に変更（または `.env` の `SHEET_NAME` に合わせる）
3. **共有** から、手順 3 の `client_email` を **編集者** で追加
4. スプレッドシート URL から ID を控える

```text
https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit
```

---

## 5. `.env` の作成

```powershell
Copy-Item config\.env.example config\.env
```

`config/.env` を編集:

```env
SPREADSHEET_ID=ここにID
GOOGLE_APPLICATION_CREDENTIALS=config/service-account.json
TIMEZONE=Asia/Tokyo
SHEET_NAME=混雑履歴
LOG_FILE=logs/run.log
```

---

## 6. 動作確認

### 取得のみ（Sheets 未設定でも可）

```powershell
uv run python -m hakata_gym_crowding.cli --dry-run --force
```

### 本番書き込み（開館時間内）

```powershell
uv run python -m hakata_gym_crowding.cli
```

初回実行時、ヘッダー行（`recorded_at` 等）が無ければ自動作成されます。

---

## 列定義（混雑履歴）

| 列 | 内容 |
|---|---|
| recorded_at | 取得実行日時（JST） |
| train_count | トレーニング室人数 |
| train_level | 混雑4段階 |
| gym_count | 体育館来場者数 |
| source_time | カウンター側計測時刻 |
| status | OK / stale_data / error 等 |

---

## トラブルシュート

| 症状 | 確認 |
|---|---|
| `SpreadsheetNotFound` | `SPREADSHEET_ID` の誤り、またはサービスアカウント未共有 |
| `Unable to load credentials` | `config/service-account.json` のパス |
| 行が増えない | 休館日・時間外で `skipped_closed` になっていないか `logs/run.log` を確認 |

---

## 関連

- 定期実行: [windows-scheduled-sync.md](windows-scheduled-sync.md)
- 要件: [doc/specs/02_要件定義.md](../../specs/02_要件定義.md)
