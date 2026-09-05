# 天気 HTML 取得（training page）

> モード: understand
> 対象: `src/hakata_gym_crowding/fetch/training_page.py`
> 最終更新: 2026-09-05

## やりたいこと

トレーニング室ページの HTML から当日の天気・気温・風・降水確率を取り出す。

## コード（D形式・標準形）

```python
def 天気を取得():
    HTML = GET(トレーニング室ページURL)  # 最大3回リトライ
    return 天気をパース(HTML)

def 天気をパース(HTML):
    アイコン = 正規表現で探す("weather_icon/xx.png")
    天気ラベル = アイコン辞書.get(アイコンコード)
    最高気温 = spanから整数(HTML, "max")
    ...
    return WeatherSnapshot(...)
```

## 用語

| 用語 | 意味 |
|---|---|
| HTML | ウェブページの本文（タグで構造化された文字列） |
| 正規表現 | 文字列のパターン検索（ここでは天気アイコン名を探す） |

## 対応する実装

| D形式の名前 | 実コードの名前 | ファイル |
|---|---|---|
| 天気を取得 | `TrainingPageFetcher.fetch_weather()` | `src/hakata_gym_crowding/fetch/training_page.py` |
| 天気をパース | `parse_weather_html()` | 同上 |
