# ドメインモデル（models）

> モード: understand
> 対象: `src/hakata_gym_crowding/domain/models.py`
> 最終更新: 2026-09-05

## やりたいこと

混雑・天気・ステータスを表すデータの入れ物（クラス）を定義する。
値は作成後に変更しない（frozen dataclass）。

## コード（D形式・標準形）

```python
class 記録状態(Enum):
    OK = "OK"
    メンテナンス = "maintenance"
    古いデータ = "stale_data"
    ...

@dataclass(frozen=True)
class 混雑スナップショット:
    取得日時: datetime
    トレーニング室人数: int
    混雑ラベル: str
    体育館人数: int
    計測時刻: str
    状態: 記録状態

@dataclass(frozen=True)
class シート1行:
  日付, 曜日, 取得時間, ...  # 16フィールド
```

## 用語

| 用語 | 意味 |
|---|---|
| dataclass | フィールドをまとめたデータの入れ物を自動生成する仕組み |
| frozen | 作成後に中身を変えられない（誤書き換え防止） |

## 対応する実装

| D形式の名前 | 実コードの名前 | ファイル |
|---|---|---|
| 記録状態 | `RecordStatus` | `src/hakata_gym_crowding/domain/models.py` |
| 混雑スナップショット | `CrowdingSnapshot` | 同上 |
| 天気 | `WeatherSnapshot` | 同上 |
| シート1行 | `CrowdingRecord` | 同上 |
