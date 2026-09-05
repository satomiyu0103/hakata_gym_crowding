# GAS 運用ルール（PoC 参照）

> **位置づけ**: SmartShelf（food-label-pdf-gas）PoC の運用要約。`gas/README.md` の代替正本（テンプレ内）。

## PDF 投入ルール

- **1 PDF = 1 商品 = 1 シート行** を運用で徹底する
- 1 PDF に複数商品が含まれる場合のコードによる複数行展開は **見送り**（GAP-A-001）
- Gemini は主対象 1 件 + `confidence_notes` で運用違反を検知する

## サイドバー操作パネル

- 一括処理・シート作成・ヘッダー再適用の 3 操作をサイドバーから実行
- `appsscript.json` に `https://www.googleapis.com/auth/script.container.ui` を明示する
- UI 追加・変更後は `authorizeContainerUi` で再認可する

## 命名対応

| 名称 | 意味 |
|---|---|
| SmartShelf | GAS / GCP 上の運用名 |
| food-label-pdf-gas | Git リポジトリ名 |

詳細:

- [sessions/2026-07-01_1pdf1product-operational-rule.md](../../ai/sessions/2026-07-01_1pdf1product-operational-rule.md)
- [sessions/2026-06-28_control-panel-sidebar.md](../../ai/sessions/2026-06-28_control-panel-sidebar.md)
- [gas-clasp-pnpm.md](gas-clasp-pnpm.md)
