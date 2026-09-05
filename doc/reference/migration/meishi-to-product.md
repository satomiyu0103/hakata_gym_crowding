# 名刺 PDF 版から商品 PDF 版への移植（PoC 参照）

> **位置づけ**: `meishi-pdf-to-sheets` から商品スキーマ向け GAS へ移植した際の方針要約。

## 背景

Phase 1 PoC として、名刺 PDF 版の GAS モジュールを商品向けに差し替え、手動 1 件（PDF → Gemini → 商品DB 追記）まで動かすことがゴールだった。

## 採用した方針

| 項目 | 採用 |
|---|---|
| 名刺版をコピーし商品向けに差し替え | ○ |
| Phase 1 で重複チェック・バッチ・Drive 移動 | ×（Phase 2 へ） |
| メニューから未実装一括処理を削除、ダミー追記メニュー追加 | ○ |
| Gemini リトライ層の移植 | ○ |

## 主なモジュール対応

| モジュール | 責務 |
|---|---|
| `setupSpreadsheet.js` | 商品DB タブ・ヘッダー 23 列 |
| `spreadsheet.js` | `appendProductRecord_`・ダミー追記 |
| `gemini.js` | 商品向けプロンプト・API・リトライ |
| `main.js` | `processPdfByFileId` 単件 E2E |
| `ui.js` | ヘッダー再適用・メニュー接続 |

詳細: [sessions/2026-06-28_phase1-poc.md](../../ai/sessions/2026-06-28_phase1-poc.md)
