# 混雑 JSON 取得（p-counter）

> モード: understand
> 対象: `src/hakata_gym_crowding/fetch/pcounter.py`
> 最終更新: 2026-09-05

## やりたいこと

公式サイトが公開する2つの JSON から人数を取り、メンテ・古いデータかどうかを判定する。

## コード（D形式・標準形）

```python
def 混雑を取得(現在時刻):
    トレーニングJSON = GETしてパース(トレーニング室URL)
    体育館JSON = GETしてパース(体育館URL)

    状態 = OK
    if トレーニングJSON.メンテ or 体育館JSON.メンテ:
        状態 = メンテナンス
    elif 計測が5分以上古い(トレーニング or 体育館):
        状態 = 古いデータ

    return スナップショット(
        人数=トレーニングJSON.人数,
        混雑ラベル=閾値からラベル(人数),
        体育館人数=体育館JSON.人数,
        状態=状態,
    )

def GETしてパース(URL):
    for 試行 in range(3):
        try:
            応答 = HTTP.get(URL)
            return JSONとして読む(応答)
        except エラー:
            待ってから再試行()
    raise RuntimeError("3回失敗")
```

## 用語

| 用語 | 意味 |
|---|---|
| JSON | データを `{ "キー": 値 }` 形式でやり取りする形式 |
| stale | 計測から時間が経ちすぎて古いとみなす状態 |

## 対応する実装

| D形式の名前 | 実コードの名前 | ファイル |
|---|---|---|
| 混雑を取得 | `PCounterFetcher.fetch_snapshot()` | `src/hakata_gym_crowding/fetch/pcounter.py` |
| GETしてパース | `_get_json()` / `_fetch_payload()` | 同上 |
| パース済み JSON（ローカル） | `parsed_json` / `parsed_response_json` / `hakata_section_json` | 同上（2026-09-06 命名改善） |
| 閾値からラベル | `crowding_level()` | `src/hakata_gym_crowding/domain/crowding.py` |
