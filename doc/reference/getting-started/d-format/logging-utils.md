# 実行ログ追記（logging）

> モード: understand
> 対象: `src/hakata_gym_crowding/logging_utils.py`
> 最終更新: 2026-09-05

## やりたいこと

`logs/run.log` にタイムスタンプ付きで1行追記する。既存の行は消さない。

## コード（D形式・標準形）

```python
def ログ追記(ログファイル, メッセージ):
    ログファイルの親フォルダを作成()
    今 = 現在日時を文字列化()
    with ログファイルを追記モードで開く() as f:
        f.write(f"{今}\t{メッセージ}\n")
```

## 対応する実装

| D形式の名前 | 実コードの名前 | ファイル |
|---|---|---|
| ログ追記 | `append_log()` | `src/hakata_gym_crowding/logging_utils.py` |
