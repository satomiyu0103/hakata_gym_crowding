---
name: my-project-design-system
description: プロジェクトのデザイン正本。色・タイポ・コンポーネント・レイアウトの参照用。
colors:
  background-primary: "#FFFFFF"      # 例: Warm Barely-There Cream
  background-secondary: "#F5F5F5"    # 例: Crisp Very Light Gray
  accent-primary: "#2563EB"          # 例: Deep Muted Teal-Navy — CTA・リンク
  text-primary: "#1A1A1A"            # 例: Charcoal Near-Black — 見出し
  text-secondary: "#6B7280"          # 例: Soft Warm Gray — 本文
  border-subtle: "#E5E7EB"           # 例: Ultra-Soft Silver Gray — 区切り線
  success: "#10B981"
  warning: "#F59E0B"
  error: "#EF4444"
  info: "#64748B"
typography:
  display: "Inter"                   # 見出し・ブランド用
  body: "Inter"                      # 本文用
  mono: "ui-monospace"               # コード・数値用（任意）
---

# Design System: [プロジェクト名]
**Project ID:** [Stitch 利用時のみ。未使用なら「なし」]

> 雛形です。`[ ]` 内を埋め、色は「描写名 + 役割 + (#HEX)」の形式で更新してください。
> Stitch 向けプロンプトでは技術用語（`rounded-lg` 等）より自然言語の描写を優先します。

## 1. Visual Theme & Atmosphere

[このプロジェクトの雰囲気を 2〜3 段落で記述。例: ミニマル / エディトリアル / ダークモード 等]

**Key Characteristics:**
- [特徴 1 — 例: 余白を広く取った落ち着いたレイアウト]
- [特徴 2 — 例: 写真・ビジュアルを主役にした構成]
- [特徴 3 — 例: 控えめなインタラクションと明確な階層]
- [特徴 4]
- [対象ユーザー・利用シーン — 例: 初回訪問者向けランディング]

## 2. Color Palette & Roles

### Primary Foundation
- **[色の描写名]** (#______ ) – 主背景。[なぜこの色か・どこに使うか]
- **[色の描写名]** (#______ ) – 副背景（カード・セクション）。[役割]

### Accent & Interactive
- **[色の描写名]** (#______ ) – プライマリ CTA・リンク・アクティブ状態。[使用箇所の制限]

### Typography & Text Hierarchy
- **[色の描写名]** (#______ ) – 見出し・強調テキスト
- **[色の描写名]** (#______ ) – 本文・補足テキスト
- **[色の描写名]** (#______ ) – ボーダー・区切り線

### Functional States
- **Success** (#10B981) – 成功・在庫あり・完了
- **Warning** (#F59E0B) – 注意・期限間近
- **Error** (#EF4444) – エラー・必須未入力
- **Info** (#64748B) – 中立メッセージ・ヒント

## 3. Typography Rules

**Primary Font Family:** [フォント名 — 例: Inter, Manrope, Noto Sans JP]  
**Character:** [フォントの性格 — 例: 幾何学的で読みやすい、和文は Noto Sans JP で補完]

### Hierarchy & Weights
| 用途 | サイズ | ウェイト | 字間・行間 | 使用箇所 |
|---|---|---|---|---|
| Display (H1) | [例: 2.5rem] | [600] | [letter-spacing / line-height] | ヒーロー・ページタイトル |
| Section (H2) | [例: 2rem] | [600] | | セクション見出し |
| Subsection (H3) | [例: 1.5rem] | [500] | | カードタイトル |
| Body | [1rem] | [400] | [line-height: 1.6〜1.7] | 本文 |
| Small / Meta | [0.875rem] | [400] | | 日付・ラベル・キャプション |
| CTA Label | [1rem] | [500] | | ボタン文言 |

### Spacing Principles
- 見出しと本文の間: [例: 0.75rem〜1rem]
- 段落間: [例: 1rem]
- セクション間: [例: 4rem〜6rem]

## 4. Component Stylings

### Buttons
- **Shape:** [例: やや丸みのある角 — 8px / pill-shaped / シャープな直角]
- **Primary CTA:** [背景色の描写名] (#______ ) + [テキスト色]。padding: [例: 0.875rem 2rem]
- **Hover:** [例: 10% 暗く / 下線 / 影を追加] — transition [例: 200ms ease]
- **Focus:** [例: 2px のアウトライン、キーボード操作向け]
- **Secondary:** [例: アウトラインのみ / ゴースト]

### Cards & Containers
- **Corner Style:** [例: 12px の緩やかな角丸]
- **Background:** [Primary / Secondary のどちらか]
- **Shadow:** [例: フラット / ホバー時のみ whisper-soft shadow]
- **Border:** [例: 1px hairline / なし]
- **Padding:** [例: 1.5rem〜2rem]

### Navigation
- **Layout:** [例: 水平 / サイドバー / ハンバーガー（モバイル）]
- **Default:** [テキスト色・ウェイト]
- **Active / Hover:** [アクセント色・下線等]
- **Spacing:** [項目間の余白]

### Inputs & Forms
- **Border:** [例: 1px Soft Gray]
- **Background:** [例: 白 / 薄いグレー]
- **Focus:** [ボーダー色変化 + リング]
- **Error state:** [赤枠 + エラーメッセージのスタイル]
- **Placeholder:** [色・トーン]

### [その他の主要コンポーネント — 必要に応じて追加]
- **例: テーブル / モーダル / タブ / バッジ**

## 5. Layout Principles

### Grid & Structure
- **Max Content Width:** [例: 1200px / 1440px]
- **Grid:** [例: 12 カラム、ガター 24px]
- **Breakpoints:**
  - Mobile: [< 768px]
  - Tablet: [768px — 1024px]
  - Desktop: [> 1024px]

### Whitespace Strategy
- **Base unit:** [例: 8px]
- **Component spacing:** [例: 16px / 24px]
- **Section margins:** [例: 5rem〜8rem]
- **Edge padding:** [モバイル / デスクトップ]

### Alignment & Responsive
- **Text alignment:** [左揃え / 中央（ヒーローのみ）等]
- **Touch targets:** 最小 [44×44px]
- **Mobile-first:** [折りたたみ・カラム数の変化]

## 6. Notes for AI / Stitch Generation

新規画面やコンポーネント生成時に参照する短いプロンプト用メモ。

### Atmosphere (一行)
> [例: Calm, editorial layout with generous whitespace and photography-first hierarchy]

### Color References (コピペ用)
- Primary CTA: [描写名] (#______ )
- Background: [描写名] (#______ )
- Text: [描写名] (#______ )

### Component Prompts (例)
- "[例: Create a primary button in Deep Muted Teal-Navy with subtly rounded corners]"
- "[例: Product card with full-bleed image and whisper-soft shadow on hover]"

### Do / Don't
- **Do:** 描写名 + hex、役割の明示、一貫した余白
- **Don't:** フレームワークのクラス名だけ（`rounded-lg` 等）をプロンプトの主語にしない

---

*Last updated: 2026-07-09 — プロジェクトルート同梱雛形。Stitch 連携後は `design-md` skill で再生成・上書き可。*
