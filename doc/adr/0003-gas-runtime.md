# ADR-0003: GAS を本番ランタイムとする

- 日付: 2026-06-28
- 状態: 採用

## 文脈

食品 PDF → Sheets PoC（SmartShelf）では、スプレッドシート連携・Drive 操作・定期トリガーが中心である。Python は補助スクリプト（検証・ローカルツール）として使う場面はあるが、本番実行環境は Google Apps Script とする。

GAS / GCP の運用名は **SmartShelf**。Git リポジトリ名は `food-label-pdf-gas` を維持する（リネームコスト回避）。

## 決定

| 項目 | 採用 |
|---|---|
| 本番ランタイム | `gas/src/`（clasp でデプロイ） |
| Python | 補助のみ（ローカル検証・スクリプト） |
| コード配置 | clasp `rootDir`: `gas/src` |

## 結果

- スプレッドシート・Drive・Slack 通知は GAS モジュールに集約
- ローカルは Node + clasp + pnpm で同期（[gas-clasp-pnpm.md](../reference/setup/gas-clasp-pnpm.md)）

詳細: [sessions/2026-06-28_smartshelf-naming-repo-split.md](../ai/sessions/2026-06-28_smartshelf-naming-repo-split.md) / [2026-06-28_clasp-rootdir.md](../ai/sessions/2026-06-28_clasp-rootdir.md)
