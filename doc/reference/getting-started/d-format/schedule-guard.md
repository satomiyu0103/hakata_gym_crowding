# 開館・休館判定（schedule guard）

> モード: understand
> 対象: `src/hakata_gym_crowding/schedule/guard.py`
> 最終更新: 2026-09-05

## やりたいこと

今が混雑取得を実行してよい時間・日かどうかを判定する。
9:00〜22:00 以外、休館日は取得しない。

## コード（D形式・標準形）

```python
def 開館判定(時刻):
    時刻 = JSTに揃える(時刻)

    if 時刻 < 9:00 or 時刻 >= 22:00:
        return 実行しない(理由=時間外)

    今日 = 時刻の日付
    if 12/28以降 or 1/4以前:
        return 実行しない(理由=年末年始)

    if 今日 == 今月の第3月曜:
        return 実行しない(理由=第3月曜休館)

    if 今日は火曜 and 昨日は祝日だった第3月曜:
        return 実行しない(理由=振替休館)

    return 実行する()
```

## 用語

| 用語 | 意味 |
|---|---|
| JST | 日本標準時（Asia/Tokyo） |
| 振替休館 | 第3月曜が祝日のとき、翌火曜に休むルール |

## 対応する実装

| D形式の名前 | 実コードの名前 | ファイル |
|---|---|---|
| 開館判定 | `ScheduleGuard.evaluate()` | `src/hakata_gym_crowding/schedule/guard.py` |
| 実行しない | `ScheduleDecision(should_run=False, ...)` | 同上 |
| 第3月曜計算 | `_third_monday()` | 同上 |
