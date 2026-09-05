# スプレッドシート追記（sheets）

> モード: understand
> 対象: `src/hakata_gym_crowding/store/sheets.py`
> 最終更新: 2026-09-05

## やりたいこと

Google スプレッドシートの「混雑履歴」シートに、16列のデータを1行追加する。

## コード（D形式・標準形）

```python
def 1行追記(レコード):
    シート = ワークシートを取得()
    値リスト = レコードを16列に変換(レコード)
    シート.append_row(値リスト)

def ワークシートを取得():
    if キャッシュあり:
        return キャッシュ

    認証 = サービスアカウントでログイン()
    ブック = スプレッドシートを開く(ID)
    try:
        シート = ブック.worksheet(シート名)
    except シート無し:
        シート = 新規作成(ヘッダー16列付き)

    if 1行目 != 正しいヘッダー:
        ヘッダーを上書き()

    キャッシュ = シート
    return シート
```

## 用語

| 用語 | 意味 |
|---|---|
| サービスアカウント | プログラム用の Google ログイン（人間ではなく bot） |
| append_row | シートの末尾に1行足す操作 |

## 対応する実装

| D形式の名前 | 実コードの名前 | ファイル |
|---|---|---|
| 1行追記 | `SheetsWriter.append_record()` | `src/hakata_gym_crowding/store/sheets.py` |
| ワークシートを取得 | `SheetsWriter._get_worksheet()` | 同上 |
| 16列に変換 | `record_to_row()` | `src/hakata_gym_crowding/domain/record_format.py` |
