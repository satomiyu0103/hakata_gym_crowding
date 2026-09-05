# レコード組立（record format）

> モード: understand
> 対象: `src/hakata_gym_crowding/domain/record_format.py`
> 最終更新: 2026-09-05

## やりたいこと

混雑スナップショットと天気を、スプレッドシート16列分の1行データに変換する。

## コード（D形式・標準形）

```python
def レコード組立(スナップショット, 天気, 天気失敗=False):
    天気データ = 天気 if 天気 else 空の天気()
    備考 = []
    if スナップショット.状態 == 古いデータ:
        備考.append("stale=計測から5分以上経過")
    if 天気失敗:
        備考.append("天気=取得失敗")

    return CrowdingRecord(
        日付=スナップショット.取得日時の日付部分,
        曜日=曜日ラベル(取得日時),
        取得時間=時刻部分,
        天気=天気データ.ラベル or "",
        ...
        備考="; ".join(備考),
    )

def 16列に変換(レコード):
    return [レコード.日付, レコード.曜日, ...]
```

## 対応する実装

| D形式の名前 | 実コードの名前 | ファイル |
|---|---|---|
| レコード組立 | `build_crowding_record()` | `src/hakata_gym_crowding/domain/record_format.py` |
| 16列に変換 | `record_to_row()` | 同上 |
| 備考組立 | `build_remarks()` | 同上 |
| 曜日ラベル | `weekday_label()` | 同上 |
