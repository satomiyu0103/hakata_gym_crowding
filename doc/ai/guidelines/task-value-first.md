# タスク価値優先（task-value-first）

Kent Beck の「[Hey, N00b, We Didn't Hire You to Complete Tasks](https://newsletter.kentbeck.com/p/hey-n00b-we-didnt-hire-you-to-complete)」を、本テンプレのエージェント運用に翻訳した背景文書である。

手順の正本は [`.cursor/skills/task-value-first/SKILL.md`](../../.cursor/skills/task-value-first/SKILL.md)。本ファイルは要約とクリティカルパスを載せる。

---

## 一行要約

タスクを最短で閉じるのではなく、要否を検証し、本質の 10% を小さな差分で出し、学びを sessions / rules に残す。

---

## B / C / A の仕分け

| 区分 | 先輩が見るもの | 代表シグナル |
|------|---------------|-------------|
| C | 信頼を損なう | 動かないコード、同じミスの再発、周囲への過大な負担 |
| B | 任せられる下限 | 動く・伝える・妥当な時間・レビューしやすい差分 |
| A | 生産性の伸び | 要否の検証、本質の特定、小さな差分列、学びの共有 |

完了数では A と B は分かれない。各タスクからどれだけ学び、周囲の仕事を楽にしたかが指標になる。

---

## クリティカルパス

```text
[C回避] 信頼の土台（動く・伝える・同ミス再発なし）
    ↓
[B確立] 任せられる実装者
    ↓
[学習] タスクごとに「なぜ・何が本質か」を掘る
    ↓
[設計] 実装前に構造を整える（Tidy First）
    ↓
[差分] 小さく・連続で・テスト付きで出す
    ↓
[共有] 学び・レビュー・文章で可視化
    ↓
[波及] ツール化・チーム外貢献（余力があるとき）
    ↓
[A] 生産性の伸びが観測される
```

並列化できないもの: 信頼なしの学び共有、学びなしのツール化、巨大な単一 diff。

---

## エージェント運用への翻訳

| Beck の段階 | 本テンプレの対応 |
|------------|-----------------|
| C 回避・B 下限 | [engineer_signals_core.mdc](../../.cursor/rules/engineer_signals_core.mdc) |
| 要否検証・差分計画 | [task-value-first/SKILL.md](../../.cursor/skills/task-value-first/SKILL.md) A-0 / A-1 |
| 実施中の比較・スコープ遵守 | task-value-first A-2 + [implementation-phase2](../../.cursor/skills/implementation-phase2/SKILL.md) |
| 小さな差分 | [git_workflow.mdc](../../.cursor/rules/git_workflow.mdc) §PR 粒度 |
| 学びの可視化 | [agent-session-record](../../.cursor/skills/agent-session-record/SKILL.md) の `## 学び` |
| 繰り返しの好み・手順 | [design-decision-record](../../.cursor/skills/design-decision-record/SKILL.md) §昇格ルール |

Phase フローとの対応:

| Phase | 追加読み込み |
|-------|-------------|
| 1 着手前 | implementation-phase1 → task-value-first（A-0・A-1） |
| 2 実施中 | implementation-phase2 + task-value-first（A-2）+ engineer_signals_core |
| 3 完了後 | agent-session-record の `## 学び` を必須にする |

---

## 関連索引

- 横断索引: [decisions/README.md](../decisions/README.md)「エージェント運用基盤」
- プロジェクトマップ: [Project_map.md](Project_map.md)
