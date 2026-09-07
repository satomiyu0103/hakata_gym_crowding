# クラウド定期実行 — 手法比較検討資料

最終更新: 2026-09-07

博多体育館混雑 RPA（`hakata_gym_crowding`）を **個人 PC 常時起動** から解放するための選択肢比較です。実装手順は [cloud-github-actions-migration.md](../../specs/plans/cloud-github-actions-migration.md) を参照してください。

---

## 1. 背景と目的

### 現状の課題

| 課題 | 内容 |
|---|---|
| PC 常時起動 | Windows タスクスケジューラ運用のため、取得のたびに PC を起動しておく必要がある |
| 画面の邪魔 | 実行時にターミナル（コマンドプロンプト）が一瞬表示される |
| 将来の拡張 | 同種の HTTP 取得タスクが増えると、タスク登録・パス管理の負荷が増大する |

### 目標

- PC を OFF にしても定期取得が動く
- 作業画面を邪魔しない
- 追加コストと運用手順を抑える
- 既存 Python 資産（`ScheduleGuard`・gspread・Slack 通知）を活かす

### 本プロジェクトの特性（移行難易度の前提）

| 項目 | 内容 |
|---|---|
| 取得方式 | HTTP のみ（`fetch/pcounter.py` の JSON API + 天気 HTML）。Selenium 不使用 |
| 保存先 | Google スプレッドシート（`store/sheets.py` / gspread） |
| 通知 | Slack Incoming Webhook（`notify/slack.py`、15 分重複抑制） |
| 実行制御 | `ScheduleGuard`（9:00–22:00 JST、休館日。`jpholiday` 使用） |
| 現状スケジュール | 30 分間隔・9:00–22:00（[windows-scheduled-sync.md](windows-scheduled-sync.md)） |
| リポジトリ | GitHub **公開** |
| 希望間隔 | **30〜60 分** |

**結論（技術面）**: ブラウザ自動化が不要なため、クラウド移行の難易度は **低〜中**（認証・状態ファイルの置き換えが主な作業）。

---

## 2. 課題の分解

3 つの痛みは **同じ解決策に必ずしも収束しない**。

| 痛み | PC ローカル改善だけ | クラウド移行 |
|---|---|---|
| PC 常時起動 | 解決しない | 解決する |
| ターミナル表示 | VBS ラッパー等でほぼ解決 | 根本解決 |
| 複数タスク管理 | タスクが増える | 1 プラットフォームに集約可能 |

---

## 3. 候補手法一覧

### A. ローカル PC のまま（移行しない選択肢）

**Windows タスクスケジューラ + 非表示起動**

- VBS で `WshShell.Run(..., 0, True)` → 黒画面フラッシュ回避
- 「ログオン時のみ」vs「ログオンしていなくても」で Session 0 実行
- バッテリー設定（`DisallowStartIfOnBatteries` 等）を明示的に OFF

| メリット | デメリット |
|---|---|
| コード変更ほぼゼロ | PC スリープ/シャットダウンで止まる |
| 既存 doc そのまま | タスクが増えると管理が線形に増加 |

**用途**: クラウド移行を決めるまでの **応急処置**。本丸（PC 不要）は未解決。

---

### B. GitHub Actions スケジュール（Python そのまま）★ 第一推奨

- `.github/workflows/*.yml` の `schedule:` + `ubuntu-latest` で `uv run python -m hakata_gym_crowding.cli`
- **公開リポジトリ** なら Linux runner 分は実質無制限
- cron は **UTC のみ**、最短 **5 分**、開始は **5〜20 分遅れる** ことがある
- 60 日間リポジトリ非アクティブで schedule 自動停止（push で復活）

| メリット | デメリット |
|---|---|
| 既存 Python をほぼそのまま使える | 時刻は UTC 換算が必要 |
| 月額 ¥0（公開 repo） | 「ちょうど 30 分おき」ではない |
| workflow 共通化で横展開しやすい | Secrets 設定が必要 |
| ログが GitHub UI に残る | egress IP はクラウドレンジ |

**本プロジェクトとの適合**: `ScheduleGuard` が開館時間外を skip するため、cron を `*/30 * * * *`（24h）にしても **ロジック上は現状と同等** にできる。

---

### C. Google Apps Script 時間トリガー（GAS へ移植）

- `UrlFetchApp.fetch` + `ScriptApp.newTrigger().timeBased()` — PC 不要
- Sheets 書き込みがネイティブ

| メリット | デメリット |
|---|---|
| Google 内完結 | Python 資産の **全面移植**（`jpholiday` → JS 等） |
| 他 GAS プロジェクトと同型 | 実行上限 **6 分/回** |
| 月額 ¥0 | Python と GAS の二重保守リスク |

**本プロジェクトとの適合**: 取得+1 行 append だけなら GAS 単体も可能だが、**既に Python MVP 完成** のため移植コスト > Actions 移行。

---

### D. マネージド cron + コンテナ（Render / Railway 等）

- Python コンテナを cron 式で起動
- Render Cron: **最低 $1/月/cron**、無料枠なし

| メリット | デメリット |
|---|---|
| 実行時間・遅延が読みやすい | 月額がかかる |
| 本番 cron 向け | 公開 GitHub がある現状では Actions が先 |

---

### E. エッジ serverless cron（Cloudflare Workers / Vercel Cron）

| サービス | 無料枠の現実 | 本件 |
|---|---|---|
| Cloudflare Workers | CPU 10ms/回（無料） | Python スクレイピング不可。JS 書き換え + 有料 Workers Paid が前提 |
| Vercel Cron | Hobby は **1 日 1 回** | 30 分間隔に不適 |

**注**: Cloudflare **Pages**（語彙クイズ等の静的配信）と **Workers Cron** は別サービス。

---

### F. 常時起動 VPS + cron（Hetzner 等）

- 月 $3〜5 程度、Linux cron で複数 Python ジョブを一括管理

| メリット | デメリット |
|---|---|
| Selenium 系も載せられる | OS パッチ・監視は自己責任 |
| 時刻精度が高い | hakata_gym 単体ではオーバースペック |

**用途**: 将来 `reportauto_lacicra` 等の **Selenium RPA** をクラウド化する見込みが強い場合の第 2 候補。

---

## 4. 比較表（本プロジェクト条件）

条件: HTTP スクレイパー / 30〜60 分 / GitHub 公開

| 手法 | PC 不要 | ターミナル問題 | Python 流用 | 月額目安 | 30〜60 分 cron | 複数タスク拡張 | 学習コスト |
|---|---|---|---|---|---|---|---|
| **A. ローカル非表示化** | × | ○ | ◎ | ¥0 | ○ | △ | 低 |
| **B. GitHub Actions** | ◎ | ◎ | ◎ | **¥0** | ○ | ◎ | 低〜中 |
| **C. GAS 時間トリガー** | ◎ | ◎ | × | ¥0 | ○ | ○ | 中 |
| **D. Render/Railway Cron** | ◎ | ◎ | ◎ | $1〜/job〜 | ◎ | ○ | 中 |
| **E. CF Workers / Vercel** | ◎ | ◎ | × | 無料不可/JS | ×/△ | △ | 高 |
| **F. VPS + cron** | ◎ | ◎ | ◎ | $3〜5 | ◎ | ◎ | 中〜高 |

---

## 5. 推奨結論

### 第一推奨: GitHub Actions（B）

| 判断軸 | 評価 |
|---|---|
| 技術適合 | Python + gspread + Slack をそのまま実行可能 |
| コスト | 公開 repo + 30 分間隔 + 1〜2 分/回 → 無料枠で十分 |
| 既存スキル | [windows-scheduled-sync.md](windows-scheduled-sync.md) の「定期起動」をサーバー側 cron に置き換えるイメージ |
| 横展開 | 将来の HTTP 系スクレイパーを workflow テンプレで追加 |

### 第二推奨: GAS（C）

Sheets 内に全部寄せたい場合のみ。Python 完成済みのため **優先度は Actions より下**。

### 第三推奨: VPS（F）

Selenium 系クラウド化が近い場合。

### 非推奨（本条件）

- Cloudflare Workers 無料（CPU 不足）
- Vercel Cron 無料（1 日 1 回上限）
- Render Cron 単独（有料・Actions で代替可）

---

## 6. 移行時の設計論点（実装前の確認）

| 現状（PC） | クラウド側の置き換え |
|---|---|
| `config/.env` + `config/service-account.json` | GitHub Secrets（SA JSON 全文・`SPREADSHEET_ID`・`SLACK_WEBHOOK_URL`） |
| `logs/.slack_notify_state.json`（重複抑制） | **Sheets の `_meta` タブ**（推奨）または Actions Cache |
| `ScheduleGuard` | **変更なし**（cron が毎回起動 → 時間外は skip で OK） |
| `logs/run.log` | Actions run log + 必要なら artifact |

### 受け入れる制約（Actions 採用時）

- cron 式は UTC（JST 9:00 = UTC 0:00 など換算）
- 開始時刻に **数分の遅延** があり得る
- 公開 repo でも Secrets に認証情報を置く（コード直書き禁止）

---

## 7. 将来の同種タスク拡張

| タスク種別 | 推奨基盤 | 例 |
|---|---|---|
| HTTP + JSON/HTML パース | GitHub Actions 共通 workflow | 本 RPA、`youtube_url_fetcher` |
| GAS 既存パイプラインの延長 | GAS トリガー | `job_db_automation` |
| Selenium / 画面操作 | VPS cron | `reportauto_lacicra` |

---

## 8. 選択チェックリスト（利用者向け）

実装に入る前に確認:

1. **PC OFF でも動かしたいか** → Yes なら B/C/D/F
2. **既存 Python を捨てたくないか** → Yes なら B/D/F
3. **月額 $0 を維持したいか** → Yes なら B または C
4. **実行時刻の精度** → ±10 分許容なら B、±1 分なら D/F
5. **1 年後に Selenium 系もクラウド化するか** → Yes なら F を視野、No なら B で十分

**本プロジェクトの前提（2026-09-07 時点）**: 間隔 30〜60 分 / GitHub 公開 → **GitHub Actions を採用**（実装計画参照）。

---

## 9. 参照（外部）

- [Scheduling Scrapers — Cron vs GitHub Actions](https://python-web-scraping.com/scaling-python-web-scrapers/deploying-scrapers-to-the-cloud/scheduling-scrapers-with-cron-and-github-actions/)
- [Deploy Python Web Scrapers — platform comparison](https://www.firecrawl.dev/blog/deploy-web-scrapers)
- [Cron Schedule: GitHub Actions / Vercel / Cloudflare](https://viadreams.cc/en/blog/cron-schedule-serverless-github-actions-vercel-cloudflare/)
- [Render Cron Jobs pricing](https://render.com/docs/cronjobs)
- [GAS time-driven triggers](https://developers.google.com/apps-script/guides/triggers/installable)
- [Task Scheduler hidden run — VBS pattern](https://dev.to/youfuhsu/exit-code-0-is-a-lie-7-ways-my-unattended-automation-silently-did-nothing-501j)

---

## 関連（リポジトリ内）

| ドキュメント | 内容 |
|---|---|
| [cloud-github-actions-migration.md](../../specs/plans/cloud-github-actions-migration.md) | 実装計画（GitHub Actions 移行） |
| [windows-scheduled-sync.md](windows-scheduled-sync.md) | 現行 PC 運用 |
| [google-sheets-hakata-crowding.md](google-sheets-hakata-crowding.md) | Sheets セットアップ |
| [slack-webhook-hakata-crowding.md](slack-webhook-hakata-crowding.md) | Slack 通知 |
