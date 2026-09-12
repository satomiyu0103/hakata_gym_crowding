# hakata_gym_crowding

福岡市立博多体育館トレーニング室の混雑状況を定期取得する RPA。

- **取得元**: [博多体育館 トレーニング室](https://ssk-hakata-gym.com/training/)
- **状態**: Phase 1 MVP 実装済
- **テンプレ**: ai-agent-devenv-template v2026.6

## 目的

トレーニング室の混雑目安と体育館来場者数を定期的に取得し、Google スプレッドシートに履歴として蓄積する。利用前に混雑傾向を把握できるようにする。

### 混雑目安（公式サイトより）

| 表示 | 目安人数 |
|---|---|
| 空いています | 0〜14人 |
| やや混雑しています | 15〜24人 |
| 混雑しています | 25〜29人 |
| 大混雑しています | 30人以上 |

## クイックスタート

```powershell
uv sync --group dev
Copy-Item config\.env.example config\.env
# config/.env と config/service-account.json を設定（下記 doc 参照）

uv run python -m hakata_gym_crowding.cli --dry-run --force
uv run python -m hakata_gym_crowding.cli
uv run pytest
```

## セットアップ

| 手順 | パス |
|---|---|
| Google スプレッドシート | [doc/reference/setup/google-sheets-hakata-crowding.md](doc/reference/setup/google-sheets-hakata-crowding.md) |
| **定期実行（GitHub Actions・推奨）** | [doc/reference/setup/github-actions-hakata-crowding.md](doc/reference/setup/github-actions-hakata-crowding.md) |
| タスクスケジューラ（レガシー・ロールバック用） | [doc/reference/setup/windows-scheduled-sync.md](doc/reference/setup/windows-scheduled-sync.md) |
| 手動実行（デスクトップショートカット） | 同上「手動実行（デスクトップ・パターン A）」 |

## ドキュメント

| 種別 | パス |
|---|---|
| Agent ルーティング | [AGENTS.md](AGENTS.md) |
| 要件・設計 | [doc/specs/](doc/specs/) |
| テンプレセットアップ | [TEMPLATE_SETUP.md](TEMPLATE_SETUP.md) |
