# hakata_gym_crowding

福岡市立博多体育館トレーニング室の混雑状況を定期取得する RPA。

- **取得元**: [博多体育館 トレーニング室](https://ssk-hakata-gym.com/training/)
- **状態**: 新規（テンプレ展開済み）
- **テンプレ**: ai-agent-devenv-template v2026.6

## 目的

トレーニング室の混雑目安（空いている / やや混雑 / 混雑 / 大混雑）を定期的に取得し、履歴として蓄積する。利用前に混雑傾向を把握できるようにする。

### 混雑目安（公式サイトより）

| 表示 | 目安人数 |
|---|---|
| 空いています | 0〜14人 |
| やや混雑しています | 15〜24人 |
| 混雑しています | 25〜29人 |
| 大混雑しています | 30人以上 |

## 次のステップ

1. 取得元ページの HTML 構造を調査し、混雑表示の取得方法を確定する
2. `doc/specs/02_要件定義.md` に FR/NFR を確定する
3. Python + uv で `src/` を初期化し、定期実行（タスクスケジューラ等）を設計する
4. Phase 1 着手時は [AGENTS.md](AGENTS.md) と [TEMPLATE_SETUP.md](TEMPLATE_SETUP.md) を参照する

## ドキュメント

| 種別 | パス |
|---|---|
| Agent ルーティング | [AGENTS.md](AGENTS.md) |
| 要件・設計 | [doc/specs/](doc/specs/) |
| テンプレセットアップ | [TEMPLATE_SETUP.md](TEMPLATE_SETUP.md) |
