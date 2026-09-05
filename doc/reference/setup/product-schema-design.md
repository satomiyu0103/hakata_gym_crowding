# 商品DB・重複キー設計（GAS PoC 参照）

> **位置づけ**: SmartShelf PoC におけるスプレッドシート重複検知の設計要約。他プロジェクトでは参考として読む。

## 重複キー優先順位

1. JAN コード
2. 商品コード
3. 複合キー（商品名等）

## 期限日の比較（FR-SHT-002）

全キー種別で `expiration_date` を比較する。

| 状況 | 挙動 |
|---|---|
| 同一キー・期限が異なる | **別行**として追記 |
| 同一キー・期限なし | 期限不問として既存行と重複判定 |
| 実装 | `baseValue` + `expirationIso` + `isDuplicateProductRecord_` |

## シート読み込みの注意

スプレッドシート上の Date 型セルを `String(date)` で読むと、期限正規化が空になり **誤って重複スキップ** する。Date 列は `yyyy-MM-dd` に変換してから比較する。

詳細: [sessions/2026-07-01_FR-SHT-002-expiration-dup-key.md](../../ai/sessions/2026-07-01_FR-SHT-002-expiration-dup-key.md)
