# ROADMAP

最終更新: {{LAST_UPDATED}}

フェーズ別の実装計画。短期の変更は [07_CHANGELOG.md](07_CHANGELOG.md) の `[Unreleased]` を参照。

機能コードの詳細は [04_機能一覧.md](04_機能一覧.md) を参照。

---

## 現在地

- Phase 2.0 完了（16列スキーマ・天気取得・移行スクリプト・コメント整備・検証設計）
- 次: 蓄積データの分析・可視化（Phase 2.1）

---

## Phase 1 — MVP（混雑取得）

| # | 内容 | 関連 FR | ステータス |
|---|---|---|---|
| 1-1 | p-counter JSON 取得 | FR-FETCH-001 | 完了 |
| 1-2 | Google Sheets 追記 | FR-STORE-001 | 完了 |
| 1-3 | 開館・休館判定 | FR-SCHED-001 | 完了 |
| 1-4 | 実行ログ | FR-LOG-001 | 完了 |
| 1-5 | Task Scheduler 手順 | FR-SCHED-001 | 完了 |

---

## Phase 2 — 分析

| # | 内容 | 関連 FR | ステータス |
|---|---|---|---|
| 2-0 | 16列スキーマ・天気取得・移行・コメント | FR-FETCH-002, FR-STORE-002 | 完了 |
| 2-1 | 曜日・時間帯別の混雑傾向集計 | — | 未着手 |
| 2-2 | 可視化（グラフ等） | — | 未着手 |
| 2-3 | イベント列の自動入力 | — | 未着手 |
| 2-4 | 障害 Slack 通知 | FR-LOG-002 | 完了 |

---

## バックログ（未割当）

| 概要 | メモ |
|---|---|
|  |  |

---

## アーカイブ（PoC 計画・参照用）

> 以下は **food-label-pdf-gas / SmartShelf PoC** の将来計画。現行テンプレの Phase 1〜2 とは別物。全文はセッション記録を参照。

### Phase 4a — 期限管理シート基盤

- `INVENTORY_SHEET_SCHEMA` 定義、期限管理タブ作成、商品DB 追記時のミラー行

### Phase 4b — Slack 期限通知

- 月初 digest（当月期限）+ 7 日前個別リマインド（FR-NTF-003 / FR-SHT-003）

### Phase 4c — 運用・検証

- 条件付き書式、在庫・ステータス更新 UI、実機検証

詳細: [sessions/2026-07-01_expiration-alert-plan.md](../ai/sessions/2026-07-01_expiration-alert-plan.md)
