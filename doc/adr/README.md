# ADR（Architecture Decision Records）

技術選定の **理由** を短く残す場所です。詳細な比較検討は `doc/ai/sessions/` に書き、ここには結論と影響範囲をまとめます。

## いつ書くか

- 採用技術・ライブラリ・構成の選定が確定したとき
- セッション記録から昇格するとき（[design-decision-record](../../.cursor/skills/design-decision-record/SKILL.md)）

## ファイル命名

```
NNNN-短い-kebab-case-タイトル.md
```

例: `0001-session-based-auth.md`

## 最小テンプレート

```markdown
# NNNN. タイトル

- 日付: YYYY-MM-DD
- 状態: 採用 / 見送り / 置換

## 文脈

（何が問題だったか）

## 決定

（何を選んだか）

## 結果

（メリット・デメリット・影響範囲）
```

## テンプレート利用時

スタック固有の ADR（例: Python ビルド・GAS ランタイム）はプロジェクト開始後に追加する。

| ADR | 概要 |
|---|---|
| [0003-gas-runtime.md](0003-gas-runtime.md) | PoC 参照: GAS 本番ランタイム |
