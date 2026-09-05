# CLI メイン処理の流れ

> モード: understand
> 対象: `src/hakata_gym_crowding/cli.py` の `main()`
> 最終更新: 2026-09-05

## やりたいこと

定期実行で混雑データを取得し、条件を満たせばスプレッドシートに1行追記する。
失敗した段階でログと Slack 通知を行い、終了コード 0 または 1 で終わる。

## コード（D形式・標準形）

```python
# 引数を読む（dry-run / force）
引数 = 引数パーサー.parse_args()

# [手順1] 設定読込
try:
    設定 = 設定を読む(dry_runならSheets不要=True)
except 設定エラー:
    画面にエラー表示()
    Slack通知できれば送る()
    終了(1)

現在時刻 = 今の日時(設定のタイムゾーン)
開館判定 = 開館ガード.判定(現在時刻)

# [手順2] 開館時間外・休館日なら取得しない
if not 引数.force:
    if not 開館判定.実行すべき:
        ログに「スキップ」と書く()
        終了(0)

# [手順3] 混雑 JSON 取得
try:
    スナップショット = 混雑取得.fetch(現在時刻)
except 取得失敗:
    ログ + Slack通知
    終了(1)

# [手順4] 天気取得（失敗しても混雑は続行）
try:
    天気 = 天気取得.fetch()
except 取得失敗:
    天気失敗フラグ = True

行データ = レコード組立(スナップショット, 天気)
画面に結果を表示()

if 引数.dry_run:
    終了(0)

if スナップショット.状態 == メンテナンス:
    終了(0)

# [手順7] Sheets 追記
try:
    シート書込.append(行データ)
except 書込失敗:
    ログ + Slack通知
    終了(1)

終了(0)
```

## 用語

| 用語 | 意味 |
|---|---|
| 終了コード | プログラムの結果。0=正常、1=エラー |
| dry-run | 取得だけしてシートに書かない試験実行 |
| force | 開館時間外でも強制実行（デバッグ用） |
| スナップショット | 取得直後の混雑1件分のデータ |

## 対応する実装

| D形式の名前 | 実コードの名前 | ファイル |
|---|---|---|
| 引数パーサー | `build_parser()` | `src/hakata_gym_crowding/cli.py` |
| main | `main()` | `src/hakata_gym_crowding/cli.py` |
| 設定を読む | `load_settings()` | `src/hakata_gym_crowding/config.py` |
| 開館ガード | `ScheduleGuard` | `src/hakata_gym_crowding/schedule/guard.py` |
| 混雑取得 | `PCounterFetcher` | `src/hakata_gym_crowding/fetch/pcounter.py` |
| 天気取得 | `TrainingPageFetcher` | `src/hakata_gym_crowding/fetch/training_page.py` |
| レコード組立 | `build_crowding_record()` | `src/hakata_gym_crowding/domain/record_format.py` |
| シート書込 | `SheetsWriter` | `src/hakata_gym_crowding/store/sheets.py` |
| Slack通知 | `notify_error()` | `src/hakata_gym_crowding/notify/slack.py` |

## 発展（E形式）

実コードでは `with PCounterFetcher() as fetcher:` のようにコンテキストマネージャ（`with`）で HTTP 接続を自動で閉じる。
