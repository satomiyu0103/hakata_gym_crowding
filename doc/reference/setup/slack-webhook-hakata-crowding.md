# Slack Incoming Webhook 設定（博多混雑 RPA）

最終更新: 2026-09-05

定期実行 CLI が **ERROR**（設定・混雑取得・Sheets 書込失敗）のときだけ Slack へ通知する手順です。

---

## 前提

- [google-sheets-hakata-crowding.md](google-sheets-hakata-crowding.md) の初回セットアップ完了
- 通知先 Slack ワークスペースで Incoming Webhook を作成できる権限があること

---

## 1. Incoming Webhook を作成

1. [Slack API](https://api.slack.com/apps) で App を作成（または既存 App を使用）
2. **Incoming Webhooks** を有効化
3. **Add New Webhook to Workspace** で通知先チャンネルを選ぶ（例: `#hakata-gym-alerts`）
4. 表示された URL をコピー（`https://hooks.slack.com/services/...`）

> Webhook URL は **パスワードと同じ** 扱い。リポジトリ・チャット・ログに貼らない。

---

## 2. `.env` に設定

[`config/.env.example`](../../../config/.env.example) を参考に、[`config/.env`](../../../config/.env) に追記する。

```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../...
SLACK_NOTIFY_ENABLED=true
```

| 変数 | 説明 |
|---|---|
| `SLACK_WEBHOOK_URL` | 空のままなら通知機能オフ |
| `SLACK_NOTIFY_ENABLED` | `false` で URL があっても送らない |

---

## 3. 通知される ERROR

| 段階 | トリガー | exit |
|---|---|:---:|
| `config` | `.env` 未設定など | 1 |
| `fetch` | p-counter JSON 取得失敗 | 1 |
| `sheets` | スプレッドシート追記失敗 | 1 |

**通知しない**: 休館スキップ、天気取得失敗（混雑は継続）、メンテナンス、成功。

同一 stage の ERROR は **15 分以内 1 通**（状態: `logs/.slack_notify_state.json`）。

---

## 4. 動作確認

### 設定 ERROR の確認（安全）

一時的に `SPREADSHEET_ID` を空にして実行する（実行後は元に戻す）。

```powershell
uv run python -m hakata_gym_crowding.cli
```

Slack に `[ERROR] 博多混雑RPA — 設定` が届くことを確認する。

### 通知を止める

- `SLACK_WEBHOOK_URL=` を空にする、または
- `SLACK_NOTIFY_ENABLED=false` にする

---

## 関連

- 定期実行（正本）: [github-actions-hakata-crowding.md](github-actions-hakata-crowding.md)
- Task Scheduler（レガシー）: [windows-scheduled-sync.md](windows-scheduled-sync.md)
- 設計: [doc/specs/03_システム設計.md](../../specs/03_システム設計.md)
- FR: `FR-LOG-002`（[04_機能一覧.md](../../specs/04_機能一覧.md)）
