# ROADMAP

最終更新: {{LAST_UPDATED}}

フェーズ別の実装計画。短期の変更は [07_CHANGELOG.md](07_CHANGELOG.md) の `[Unreleased]` を参照。

機能コードの詳細は [04_機能一覧.md](04_機能一覧.md) を参照。

---

## 現在地

- テンプレート初期状態（`src/` は README のみ。スタック未選定）
- 次のマイルストーン: {{CURRENT_VERSION}} のスコープを [02_要件定義.md](02_要件定義.md) で確定する

---

## Phase 1 — （記入式）

| # | 内容 | 関連 FR | ステータス |
|---|---|---|---|
| 1-1 |  | FR-XXXX-001 | 未着手 |

---

## Phase 2 — （記入式）

| # | 内容 | 関連 FR | ステータス |
|---|---|---|---|
| 2-1 |  |  | 未着手 |

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
