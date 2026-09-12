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

初回実行時、ヘッダー行（16列・日本語）が無ければ自動作成されます。

### 旧スキーマからの移行（英語6列 → 日本語16列）

既存シートに `recorded_at` 等の旧ヘッダーがある場合、**先に**移行スクリプトを実行してください。

```powershell
# 変換内容の確認のみ
uv run python scripts/migrate_sheet_columns.py --dry-run

# 本番移行（シート全体を上書き。事前にスプレッドシートのバックアップを推奨）
uv run python scripts/migrate_sheet_columns.py
```

---

## 列定義（混雑履歴・全16列）

| # | 列 | 型 | 内容 |
|---|---|---|---|
| 1 | 日付 | 文字列 | 取得日（JST）`YYYY-MM-DD` |
| 2 | 曜日 | 文字列 | `月`〜`日` |
| 3 | 取得時間 | 文字列 | RPA 実行時刻 `HH:MM:SS` |
| 4 | 計測時間 | 文字列 | カウンター側計測時刻 `HH:MM:SS`（JSON `time_calc`） |
| 5 | 天気 | 文字列 | 晴れ・曇り・雨など（サイト天気アイコンから変換） |
| 6 | 最高気温 | 数値 | 当日最高（℃） |
| 7 | 最低気温 | 数値 | 当日最低（℃） |
| 8 | 風速 | 数値 | m/s |
| 9 | 風向 | 文字列 | 東・南西など |
| 10 | 降水確率 | 数値 | 0〜100（% はセルに含めない） |
| 11 | ステータス | 文字列 | OK / stale_data / maintenance 等 |
| 12 | トレーニングルーム利用者数 | 数値 | 人数 |
| 13 | 混雑レベル | 文字列 | 4段階ラベル |
| 14 | 体育館利用者数 | 数値 | 来場者数 |
| 15 | イベント | 文字列 | 将来用（初期は空欄） |
| 16 | 備考 | 文字列 | stale 理由、天気取得失敗時の注記 |

**分析の目安**: 混雑・天気の時間軸は **計測時間**、定期実行の監査は **取得時間** を使う。

---

## トラブルシュート

| 症状 | 確認 |
|---|---|
| `SpreadsheetNotFound` | `SPREADSHEET_ID` の誤り、またはサービスアカウント未共有 |
| `Unable to load credentials` | `config/service-account.json` のパス |
| 行が増えない | 休館日・時間外で `skipped_closed` になっていないか `logs/run.log` を確認 |

---

## 関連

- 定期実行（正本）: [github-actions-hakata-crowding.md](github-actions-hakata-crowding.md)
- 定期実行（レガシー）: [windows-scheduled-sync.md](windows-scheduled-sync.md)
- 要件: [doc/specs/02_要件定義.md](../../specs/02_要件定義.md)
