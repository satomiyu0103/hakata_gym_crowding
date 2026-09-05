# 混雑ラベル算出（crowding）

> モード: understand
> 対象: `src/hakata_gym_crowding/domain/crowding.py`
> 最終更新: 2026-09-05

## やりたいこと

人数と4段階の閾値から、サイトと同じ日本語の混雑ラベルを返す。

## コード（D形式・標準形）

```python
def 混雑ラベル(人数, 閾値):
    if 人数 >= 閾値.rank4:
        return "大混雑しています"
    if 人数 >= 閾値.rank3:
        return "混雑しています"
    if 人数 >= 閾値.rank2:
        return "やや混雑しています"
    return "空いています"
```

## 対応する実装

| D形式の名前 | 実コードの名前 | ファイル |
|---|---|---|
| 混雑ラベル | `crowding_level()` | `src/hakata_gym_crowding/domain/crowding.py` |
