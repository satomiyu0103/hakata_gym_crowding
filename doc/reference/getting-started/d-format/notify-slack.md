# Slack エラー通知

> モード: understand
> 対象: `src/hakata_gym_crowding/notify/slack.py`
> 最終更新: 2026-09-05

## やりたいこと

設定・取得・Sheets 書込のいずれかで失敗したとき、Slack に ERROR メッセージを送る。
同じエラーは15分間は再送しない。通知自体が失敗しても本処理は止めない。

## コード（D形式・標準形）

```python
def エラー通知(設定, run_id, 段階, 例外):
    if not 設定.Slack有効 or Webhook未設定:
        return  # 何もしない

    詳細 = 秘密情報をマスク(str(例外))
    if 15分以内に同じエラーを送済み(段階, 詳細):
        return

    メッセージ = 組立(run_id, 段階, 詳細, 次のアクション)
    try:
        WebhookにPOST(メッセージ)
        送信時刻を記録()
    except:
        ログに warn のみ
```

## 用語

| 用語 | 意味 |
|---|---|
| Webhook | URL に POST すると Slack チャンネルに投稿される仕組み |
| 重複抑制 | 同じエラーを短時間に何度も送らないこと |

## 対応する実装

| D形式の名前 | 実コードの名前 | ファイル |
|---|---|---|
| エラー通知 | `notify_error()` | `src/hakata_gym_crowding/notify/slack.py` |
| 15分判定 | `_should_notify()` | 同上 |
| WebhookにPOST | `_post_webhook()` | 同上 |
