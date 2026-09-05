# 読みやすいコードコメント規約（開発テンプレ正本）

> Agent が生成するコードは、**処理の流れと意図**が追えることを最優先にする。コメントは日本語。自明な import・getter・1 行代入には書かない。

## 適用範囲

| 層 | 参照 |
|---|---|
| Rule（globs 適用） | `.cursor/rules/code_comments.mdc` |
| 読み方 | `.cursor/rules/junior_code_reading.mdc` |
| Skill（手順・例） | `.cursor/skills/readable-code-comments/SKILL.md` |
| ブロック内コメント | `.cursor/skills/junior-code-comments/SKILL.md` |
| stop フック | `.cursor/hooks/check-code-comments.py` |

対象パス: `src/**` · `scripts/**` · `tampermonkey/**` · `**/*.user.js` · `gas/**` · `notebooks/**`（DS テンプレ）

## 三層モデル（L1 / L2 / L3）

| 層 | 書く場所 | 内容 |
|---|---|---|
| **L1** | モジュール docstring | 番号付きステップ + 各ステップの失敗時の扱い |
| **L2** | 関数 docstring | 受け取る / 返す / 処理の流れ / 例外・終了コード |
| **L3** | 制御構文直前 | 条件 → 結果。重要 `try` は P4 分岐表 |

## flow_focused 方針

- **厚く**: `cli.py`、外部 API・Sheets・Slack 境界の `try/except`
- **1文**: 単純な `if`（閾値比較など）
- **D形式**: `doc/reference/getting-started/d-format/`（英語識別子の補助）

## 4 層（骨格）

| 層 | 書く場所 | 内容 |
|---|---|---|
| **モジュール** | ファイル冒頭 | L1 と同義 |
| **クラス** | クラス直前 / docstring | 目的・集まるデータと処理・バリデーション有無 |
| **自作関数** | 関数直前 / docstring | L2 と同義 |
| **共通** | 非自明な行の直前 | L3 と同義 / エラー修正時の意図 |

## 1. 共通

| 種類 | いつ書く | 書く内容 |
|---|---|---|
| **処理の意図** | 重要な `if` / `for` / `try` ブロック直前 | 条件 → 結果（1〜3 行） |
| **エラー修正時の意図** | バグ修正・ワークアラウンド・`try/except` の直前 | 以前の問題・今回の対処・他への影響 |

## 適用の目安

| ティア | 対象 | 義務 |
|:---:|---|---|
| A | 触ったファイルの新規関数・クラス | モジュール冒頭 + 関数/クラスヘッダ |
| B | 重要な `if` / `for` / `try` | ブロック直前に L3 |
| C | 1 行ヘルパー | 関数ヘッダのみ |

## 関連

- [junior-code-comments](../../../.cursor/skills/junior-code-comments/SKILL.md)
- [junior-code-reading](../../../.cursor/skills/junior-code-reading/SKILL.md)
- [読み方.md](../../../doc/reference/getting-started/読み方.md)
- [d-format-code-guide](../../../.cursor/skills/d-format-code-guide/SKILL.md)
