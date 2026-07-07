<p align="center">
  <img src="docs/assets/banner.svg" alt="Research Agent — Energy & Power Engineering" width="420">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python"></a>
  <a href="https://github.com/1844514356zjc-dev/research-agent/actions/workflows/ci.yml"><img src="https://github.com/1844514356zjc-dev/research-agent/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/powered_by-Claude-D97757.svg" alt="powered by Claude">
</p>

<p align="center">
  <a href="README.md">简体中文</a> · <a href="README.en.md">English</a> · <b>日本語</b> · <a href="README.es.md">Español</a> · <a href="README.de.md">Deutsch</a>
</p>

> **エネルギー・動力工学向け CLI リサーチアシスタント — 文献精読・論文推敲・査読・研究評価。**

**エネルギー・動力工学**の研究者向けコマンドラインツール。ターミナル一つで、**文献検索と精読、論文の執筆と推敲、査読・アイデア評価**という日常作業をこなします。システムプロンプトにはランキン/ブレイトン/コンバインドサイクル、ORC、sCO₂、HRSG、エクセルギー解析などの領域知識と、主要ターゲットジャーナル（Energy、Applied Energy、Applied Thermal Engineering、ECAM、ASME JEGTP）の文体が組み込まれています。

Claude API を駆動源に使い、文献検索はすべて**無料の学術 API**（OpenAlex / Crossref / Semantic Scholar / arXiv / Unpaywall）で行うため、追加の API キーは不要です。ノートや原稿、査読記録はローカルの `workspace/` に残り、外部にアップロードされません。

> 🌐 **言語に関する注意:** 本エージェントは**既定で中国語出力**（専門用語は英語）になります。日本語で答えてほしい場合はその都度指示してください（例：*「日本語で答えて」*）。既定を変更するには [`prompts.py`](prompts.py) のプロンプトを編集します。
>
> 📝 本翻訳は権威ある[中文オリジナル (README.md)](README.md) より遅れる場合があります。

---

## なぜこのツールか

AI リサーチツールは既に多数ありますが、本ツールはいくつか異なる判断をしています：

- **検索コストゼロ** — 有料検索に依存せず、Anthropic の web_search も使いません。学術 API のほうが精度が高く、学術的で、完全に無料です。
- **マルチソース統合** — `source="all"` で OpenAlex + Crossref + Semantic Scholar + arXiv の結果を DOI+タイトルで重複排除し、引用数でランク付け。手動での重複整理も、単一 DB のバイアスも不要です。
- **領域知識を内蔵** — サイクル構成、主要指標（熱効率・エクセルギー効率・抽気率）、物性データの出所、よくある方法論の落とし穴（エクセルギー収支の不一致、作動流体の絞り込みが狭い、基準ケースとの比較がない等）をプロンプトに書き込んでおり、毎回教え直す必要がありません。
- **データはローカル** — あなたが能動的に行う Claude 呼び出しと学術検索以外にアップロードは一切なし。`workspace/` はカレントディレクトリにあり、いつでも確認・編集・バックアップできます。
- **セッションをまたぐ蓄積** — ノート・原稿・査読記録は markdown で保存され、キーワード検索でいつでも引き出せます。使うほどに便利になります。
- **PDF を自分で読む** — ローカル PDF でも DOI でも与えれば、自らダウンロード・解析・精読し、ノートを作成します。

## 対象読者

- エネルギー・動力工学および周辺分野（再生可能エネルギー、原子力、冷凍・空調、サーマルマネジメント、マルチエネルギーシステム）の大学院生・博士・若手研究者
- 「新規論文を素早く理解する」「日本語の方法章を投稿用の英語にする」「投稿前に自己点検する」ことがよくある人
- コマンドラインに慣れており、自身の API キーを持ち（直連または代理経由）、原稿やデータを Web ツールに貼りたくない人

> 不向きな人：GUI が必要な方、API キーをお持ちでない方、API の費用をツール側に負担させたい方。

## 主な機能

| 機能 | 内容 |
|---|---|
| 📚 文献精読 | マルチソース検索 + 重複排除 + 引用ランク付け。OA PDF をダウンロードし、バイリンガルノートを自動保存 |
| ✍️ 執筆・推敲 | 日英の学術リライト、対象ジャーナルの文体調整、査読コメントへの point-by-point 返答、長文の一括推敲 |
| 🔍 査読・アイデア評価 | 新規性 / 厳密性 / 明瞭性 / 意義 の 4 軸採点 + 行レベルの指摘 + major/minor リスト |
| 🧠 領域知識 | エネルギー・動力工学の用語、ジャーナル情報、方法論の落とし穴をプロンプトに内蔵 |
| 🗂️ セッション横断ノート | `workspace/` 内の全 markdown をキーワード検索 |
| 🔌 無料データ源 | OpenAlex / Crossref / Semantic Scholar / arXiv / Unpaywall（キー不要） |
| 🛡️ 書き込みサンドボックス | ファイル書き込みは `workspace/` 配下に限定 |

---

## インストール

Python 3.11+ と API キーが必要です（直連なら Anthropic、代理経由なら代理のキー）。

### 方法 A：pipx（推奨、分離インストール）

```bash
pipx install git+https://github.com/1844514356zjc-dev/research-agent.git
```

`research-agent` コマンドが使えるようになります。`workspace/` は**実行したディレクトリ**に作成されます。

### 方法 B：pip

```bash
pip install git+https://github.com/1844514356zjc-dev/research-agent.git
```

### 方法 C：ソースから（開発向け）

```bash
git clone https://github.com/1844514356zjc-dev/research-agent.git
cd research-agent
pip install -r requirements.txt
```

### API キーの設定

**実行するディレクトリ**に `.env` を作成します（環境変数は任意の方法で設定可能）：

```bash
cp .env.example .env   # または新規作成
# .env を編集：
#   ANTHROPIC_API_KEY=sk-ant-...        （必須 — Anthropic のキー、または代理のキー）
#   UNPAYWALL_EMAIL=you@your-school.edu  （任意、実在アドレス。OA PDF 検索が改善）
#   MODEL=claude-sonnet-5                （任意、既定モデルを上書き）
```

> `.env` は `.gitignore` 済みでコミットされません。

---

## クイックスタート（30 秒）

```bash
cd ~/my-research        # 任意の作業ディレクトリ
research-agent literature
```

あとは質問を入力するだけです：

```
你: 過去5年の sCO2 ブレイトンサイクルの高引用論文を検索し、最も引用の多い1編を精読して日本語でノートを作成
```

マルチソース検索 → 重複排除とランク付け → OA PDF を検索 → ダウンロードして精読 → `workspace/notes/` にバイリンガルノートを生成、まで自動で行います。ストリーミング出力なので、ツールの呼び出しや読み取り内容をその場で確認できます。

---

## 使い方

起動：

```bash
research-agent                       # モードを対話選択
research-agent literature            # 文献モードへ直接起動
research-agent writing --model opus  # 執筆モード + opus
research-agent review  --model opus  # 査読には opus が推奨
```

> ソース実行の場合、`research-agent` を `python main.py` に読み替えてください。

### モード 1：文献検索と精読（`literature`）

最もよく使うモード。例：

- `ORC の作動流体選択に関するレビューを検索（直近5年・高引用）`
- `DOI 10.1016/j.energy.2019.115900 は何を扱った論文？ 日本語でノートを`
- `以前に読んだ R245fa 関連論文は？`（ローカルノートを自動検索）

### モード 2：執筆と推敲（`writing`）

- 方法章を貼り付け：`Applied Energy の文体で英語に書き直して。数値と単位は維持`
- 査読コメントを貼り付け：`point-by-point で返答、専門的トーンで`
- 長文の一括推敲は `/rewrite` を参照

### モード 3：査読 / アイデア評価（`review`）

- `/pdf ~/Downloads/manuscript.pdf`
- `新規性と方法の厳密性を評価。major/minor リストを作成`
- 出力：4 軸採点（1〜5）+ 行レベル指摘 + 実行可能な改善案 + 総合判定（受入/小修正/大修正/却下）

### コマンドリファレンス

REPL 内では `/` で始まるコマンドが使えます：

| コマンド | 機能 | 例 |
|---|---|---|
| `/pdf <path...>` | 1 つ以上の PDF を事前読込（glob 対応） | `/pdf ~/Downloads/*.pdf` |
| `/rewrite <path> [--to en\|zh] [--style "..."]` | md/txt を節ごとに一括推敲し、`-en`/`-zh` のサフィックスで保存 | `/rewrite drafts/methods.md --to en --style "Applied Energy"` |
| `/notes [keywords]` | ノート一覧、またはキーワード検索 | `/notes orc fluid` |
| `/mode <mode>` | モード切替（履歴クリア） | `/mode writing` |
| `/model <name>` | モデル切替：`sonnet`/`opus`/`haiku` または完全 id | `/model opus` |
| `/save <name>` | 会話を `workspace/notes/` に保存 | `/save orc-survey` |
| `/clear` | 現在の履歴をクリア | |
| `/help` `/quit` | ヘルプ / 終了 | |

---

## ツールとデータ源

会話の中でエージェントが適宜呼び出すツール（名前で指定することも可能）：

**検索系（すべて無料・キー不要）**

| ツール | ソース | 用途 |
|---|---|---|
| `search_papers` | OpenAlex / Crossref / Semantic Scholar / arXiv | キーワード検索。`source="all"` は統合して引用数でランク付け |
| `get_citations` | Semantic Scholar | 被引用 / 参考文献の取得 |
| `get_open_pdf` | Unpaywall | DOI から合法 OA PDF の URL を取得 |

**ローカル系**

| ツール | 用途 |
|---|---|
| `read_pdf` | ローカル PDF のテキスト抽出。`pages="1-5"`、`"2,4,6"` も可 |
| `download_pdf` | URL の PDF を `workspace/papers/` にダウンロード |
| `read_file` / `write_file` | ローカルテキストの読み書き（書き込みは `workspace/` 内限定） |
| `search_notes` / `list_notes` | ノートのキーワード検索 / 全ノート一覧 |

---

## 設定

設定はすべて環境変数（`.env` またはシェル）経由：

| 変数 | 必須 | 説明 |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | Claude の API キー |
| `MODEL` | — | 既定 `claude-sonnet-5`。査読には `claude-opus-4-8` を推奨 |
| `UNPAYWALL_EMAIL` | — | OA 検索の連絡先メール。**実在アドレス**を使用（`example.com` は拒否されます） |

**モデル選択:** 日常の検索・精読・執筆は `sonnet`（速く安価）。深い査読には `opus`（遅く高価だが推論が深い）。

---

## 典型的ワークフロー

### ① 企画書のための文献展望

```bash
research-agent literature
你: 超臨界 CO2 再圧縮ブレイトンサイクル＋太ーラの高引用論文を直近5年で検索、重複排除して上位10件
你: 1, 3, 7番目を精読して各ノート作成
你: これら全体を統合して研究ギャップ分析
你: /save sco2-solar-survey
```

### ② 日本語の方法章 → Applied Energy 英文

```bash
research-agent writing
你: /rewrite drafts/methods-ja.md --to en --style "Applied Energy"
```

節ごとに「原文要点 → 推敲」の対比を出し、データ・単位・記号・式番号を維持。成果物は `drafts/methods-ja-en.md` に保存。

### ③ 投稿前の自己査読

```bash
research-agent review --model opus
你: /pdf ~/Downloads/manuscript.pdf
你: Energy 誌の基準で評価、新規性と厳密性を中心に major/minor リスト
你: /save self-review-v1
```

---

## 実行例（参考）

文献精読の対話例（出力は参考であり、実機のスクリーンショットではありません）：

```
Research Agent · Energy & Power Engineering
Mode: literature   Model: claude-sonnet-5   Workspace: /Users/me/my-research/workspace

你: ORC の作動流体に関する高引用論文を検索。最上位を精読。

→ calling 1 tool: search_papers
Source: all (multi-source dedup, 3/4 sources responded) | Query: organic rankine cycle working fluid
5 results after dedup (ranked by citations)
1. Effect of working fluids on organic Rankine cycle for waste heat recovery (2004) [cited=761]
   DOI: 10.1016/j.energy.2004.01.004 ...
→ calling 2 tools: get_open_pdf, read_pdf

最も引用の多い Liu & Chien (2004) を精読：
[Research question] 低品位廃熱回収向け ORC において作動流体が性能にどう影響するか …
[Method] 同一境界条件で11種の作動流体を熱力学的に比較 …
[Key finding] R245fa が 120°C 熱源で最高熱効率(8.5%) …
[Limitation] 熱安定性の上限を考慮していない …
[Implication] …

→ written to: workspace/notes/liu-2004-orc-working-fluids.md  (1.8KB)
```

---

## プロジェクト構成

```
research-agent/
├── main.py            # CLI エントリ + REPL + スラッシュコマンド
├── agent.py           # ストリーミング tool-calling ループ
├── tools.py           # 9 ツール + JSON スキーマ（検索/ローカル/ノート）
├── prompts.py         # 3 モードのプロンプト + 領域知識
├── test_offline.py    # オフライン確定テスト（CI で実行）
├── pyproject.toml     # パッケージ設定 + research-agent エントリ
├── requirements.txt
└── workspace/         # 実行時出力（gitignore）、カレントで自動作成
    ├── notes/         # 文献ノート、会話アーカイブ
    ├── drafts/        # 執筆・推敲成果物
    ├── reviews/       # 査読記録
    └── papers/        # ダウンロードした PDF
```

---

## FAQ

**インターネットは必要？** はい。検索は学術 API、推敲は Claude API を使います。ローカル PDF の読み取りのみ不要です。

**API 費用の目安は？** 主なコストは Claude。Sonnet で文献精読1回（ツール呼び出し数回込み）は通常数百〜数千トークン、数円程度。Opus は約 5〜15 倍高価なので、深い査読時に使います。

**レートリミット（429）になる？** Semantic Scholar と OpenAlex は認証なしリクエストを制限します。`source="all"` は失敗ソースをスキップして残りで補完します。しばらくして再試行してください。`UNPAYWALL_EMAIL` に実在アドレスを入れると polite pool に入り制限が緩みます。

**課金論文も読める？** オープンアクセス（OA）の全文のみ。非 OA 論文はメタデータ（タイトル/著者/年/DOI/引用数/抄録）まで取得できますが、PDF はダウンロードできません（著作権の制約）。

**ノートはどこに保存？** **実行したディレクトリ**の `workspace/` に、プレーン markdown で。別ディレクトリで実行すれば別の workspace になります。

**他分野にも使える？** 領域知識は [`prompts.py`](prompts.py) の `DOMAIN_KNOWLEDGE` にあります。ここを書き換えれば化学・材料・機械など他分野にも転用可能。検索・執筆ツール自体は分野非依存です。

**会話履歴の保持期間は？** 現セッションのメモリ内のみ。`/save` でアーカイブ可能。次回起動は新規セッションですが、`workspace/` のノートは永続します。

---

## 既知の制限

- API キーが必要（直連 Anthropic または代理経由、従量課金・自己負担）
- 既定出力言語は中国語（指示で切替可能、`prompts.py` で既定変更も可）
- ノート検索はキーワード一致（ベクトル意味検索ではない）
- OA の全文 PDF のみ取得可能（非 OA はメタデータのみ）
- arXiv / Semantic Scholar は稀に不安定・制限あり（コード側で優雅に縮退）

---

## コントリビュート

Issue・PR 歓迎。小さな修正はそのまま PR を。大きな変更は方向性を先に Issue でご相談ください。

テスト実行：

```bash
python test_offline.py            # オフライン確定テスト（ネットワーク/キー不要）
python -m py_compile *.py         # 構文チェック
```

CI はプッシュ毎に Python 3.11〜3.14 のマトリクスを実行します。

---

## ライセンス

[MIT](LICENSE)
