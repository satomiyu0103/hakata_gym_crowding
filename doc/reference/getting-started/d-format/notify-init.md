# 通知パッケージ（notify）

> モード: understand
> 対象: `src/hakata_gym_crowding/notify/__init__.py`
> 最終更新: 2026-09-05

## やりたいこと

`notify` フォルダが「障害通知」用であることを示すパッケージ宣言。

## コード（D形式・標準形）

```python
"""障害通知パッケージ — Slack Incoming Webhook による ERROR 通知。"""
# 実装の本体は slack.py にある
```

## 対応する実装

| D形式の名前 | 実コードの名前 | ファイル |
|---|---|---|
| 通知パッケージ | `notify` パッケージ | `src/hakata_gym_crowding/notify/__init__.py` |
| Slack 通知 | `notify.slack` | `src/hakata_gym_crowding/notify/slack.py` |
