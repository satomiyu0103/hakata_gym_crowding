# 変数命名インベントリ — 運用方法（テンプレ正本）

最終更新: 2026-09-06

## 目的

`variable-naming-inventory.md` を **プロジェクト固有の命名台帳** として統一的に運用する。  
一括リネームは行わず、既存違反の可視化と「触ったときだけ直す」改善を回す。

## 三層の役割分担

| 層 | パス | 同期 | 内容 |
|---|---|---|---|
| 規約 | `.cursor/rules/naming_conventions.mdc` | テンプレ overwrite | 禁止語・推奨パターン・許容リスト |
| 手順 | `.cursor/skills/junior-friendly-naming/SKILL.md` | テンプレ overwrite | チェックリスト・リネーム手順 |
| **運用正本** | **本ファイル** | テンプレ overwrite | いつ書く・表形式・優先度・hook 連携 |
| **プロジェクト台帳** | `variable-naming-inventory.md` | copy_if_missing + exclude | 語彙・違反・例外・良い例（業務固有） |
| 差分ギャップ | `.cursor/doc/variable_naming_gaps.md` | stop フック自動 | 当ターン diff の禁止語のみ |

```text
新規コード → hook が gaps に記録 → 修正 → gaps [x]
既存違反   → inventory に棚卸し → 触ったときに修正 → inventory [x]
```

## いつ inventory を触るか

| タイミング | 作業 |
|---|---|
| **初回棚卸し** | 命名 hook 導入後、`src/`（必要なら `tests/` `scripts/`）を禁止語で grep し、違反一覧・語彙・良い例を `variable-naming-inventory.md` に転記 |
| **ファイル変更時** | 触ったファイルの inventory 行を修正し、解消したら `[x]` に更新（**行は削除しない**） |
| **新規違反の発見** | 違反一覧に行を追加。理由列を必ず書く |
| **語彙の追加** | ドメイン語が増えたら語彙表に追記 |

**しないこと**: 台帳を見て一括リネーム PR を切る（スコープ外。触った範囲のみ）。

## 表スキーマ（固定）

### 違反一覧

| 列 | 内容 |
|---|---|
| 状態 | `[ ]` 未対応 / `[x]` 解消済み |
| 優先度 | 高 / 中 / 低（下表） |
| ファイル | `src/...` からの相対パス。行番号が分かれば `L103` 併記 |
| 現行名 | 変数・引数名 |
| 推奨名 | 改名後の候補 |
| 理由 | 禁止語・単体汎用名・型名混同 等 |

### 例外（維持）

| 列 | 内容 |
|---|---|
| ファイル | パス |
| 名前 | 維持する識別子 |
| 理由 | 外部 API 境界・argparse 慣習 等 |

### 良い例（踏襲）

| 列 | 内容 |
|---|---|
| ファイル | パス |
| 名前 | 識別子 |
| パターン | `{場所}_{属性}` 等 |

### プロジェクト語彙

| 列 | 内容 |
|---|---|
| 語彙 | 英語 snake_case の単語 |
| 意味 | 日本語で1行 |

## 優先度の定義

| 優先度 | 基準 | 例 |
|---|---|---|
| **高** | 禁止語リストに該当、または誤解でバグりやすい | `data`, `payload`（ローカル） |
| **中** | 単体汎用名。文脈追跡が必要 | `count`（引数）, `state` |
| **低** | スコープが短く、周辺コードで補える | `line`（直後に print する1行） |

## gaps との連携

1. stop フック（`check-variable-naming.py`）は **git diff の追加行のみ** 検査する
2. `variable_naming_gaps.md` に pending が出たら [junior-friendly-naming/SKILL.md](../../../.cursor/skills/junior-friendly-naming/SKILL.md) で修正
3. 解消後 gaps の行を `[x]` にする
4. **同じ違反が既存コードにもある**場合は、初回棚卸しまたは発見時に inventory へも行を追加する（gaps は一時、inventory は恒久台帳）

## publish との関係

| ファイル | publish 時 |
|---|---|
| 本ファイル（ops） | テンプレから **上書き** される |
| `variable-naming-inventory.md` | **上書きされない**（exclude）。新規プロジェクトのみ stub が配布 |
| `.cursor/rules` / skills / hooks | テンプレから上書き |

**博多体育館など業務固有の例は inventory にのみ書く。** rule / skill に書くと次回 publish で消える。

## 初回棚卸し手順

1. [naming_conventions.mdc](../../../.cursor/rules/naming_conventions.mdc) の禁止語リストを確認
2. `src/` を grep（例: `data`, `payload`, `count`, `node` 等）
3. `variable-naming-inventory.md` を新規作成または更新
   - プロジェクト語彙表
   - 違反一覧（grep 結果を転記）
   - 例外（外部 JSON フィールド等）
   - 良い例（既存の良い命名を3件以上）
4. [junior-friendly-naming/SKILL.md](../../../.cursor/skills/junior-friendly-naming/SKILL.md) のチェックリストで新規コードを運用開始

## DS 分析プロジェクト向け（ds-analysis-template）

| 項目 | 内容 |
|---|---|
| 対象パス | `src/`・`notebooks/` の Python ローカル変数 |
| データフレーム | `df` 単体は避け、`train_df`・`merged_orders_df` 等の複合名 |
| 台帳 | 同一ファイル名 `variable-naming-inventory.md` をプロジェクトルートの `doc/ai/guidelines/` に置く |
| hook | DS テンプレに naming hook 未導入の場合は、手動チェック + 本 ops に従う |

## 関連

- 命名規約: [naming_conventions.mdc](../../../.cursor/rules/naming_conventions.mdc)
- 手順: [junior-friendly-naming/SKILL.md](../../../.cursor/skills/junior-friendly-naming/SKILL.md)
- プロジェクト台帳: [variable-naming-inventory.md](variable-naming-inventory.md)
