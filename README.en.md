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
  <a href="README.md">简体中文</a> · <b>English</b> · <a href="README.ja.md">日本語</a> · <a href="README.es.md">Español</a> · <a href="README.de.md">Deutsch</a>
</p>

A CLI research assistant for **energy & power engineering** researchers. Handle three everyday tasks in one terminal: **literature search & deep-read, paper writing & polishing, review & idea evaluation**. The system prompts embed domain knowledge — Rankine/Brayton/combined cycles, ORC, sCO₂, HRSG, exergy analysis — and the writing styles of target journals (Energy, Applied Energy, Applied Thermal Engineering, ECAM, ASME JEGTP). Search runs on **free academic APIs** (no extra keys); your notes, drafts, and reviews stay in a local `workspace/`.

<p align="center"><sub><b>Install in 30 seconds</b></sub></p>

```bash
pipx install git+https://github.com/1844514356zjc-dev/research-agent.git
research-agent   # first run launches a setup wizard: key / output language / model
```

## Contents

|  |  |
|---|---|
| 🤔 [Why use it](#why-use-it) | ⚡ [Quick start](#quick-start-30-seconds) |
| 👤 [Who it's for](#who-its-for) | 📦 [Installation](#installation) |
| ✨ [Features](#features) | 📖 [Usage](#usage) |
| 🛠️ [Tools & data sources](#tools--data-sources) | 🧩 [Architecture](#architecture) |
| ⚙️ [Configuration](#configuration) | 🧪 [Typical workflows](#typical-workflows) |
| ❓ [FAQ](#faq) | ⚠️ [Limitations](#limitations) |
| 🤝 [Contributing](#contributing) | 📄 [License](#license) |

> 🌐 **Language note:** The agent **defaults to Chinese output** (with English technical terms) — or whatever your system language detects to. Switch any of these ways: set `OUTPUT_LANG` (`zh`/`en`/`ja`/`es`/`de`), pick it in the first-run wizard, or run `/lang en` mid-session.
>
> 📝 Translations of this README may lag behind the authoritative [中文原版 (README.md)](README.md).

---

## Why use it

Plenty of AI research tools exist. This one makes a few different trade-offs:

- **Zero retrieval cost** — No paid search; it doesn't even use Anthropic's own web_search. Academic APIs are more precise, more scholarly, and completely free.
- **Multi-source dedup** — `source="all"` merges results from OpenAlex + Crossref + Semantic Scholar + arXiv, dedupes by DOI + title, and ranks by citation count. No manual de-duplication; no single-database bias.
- **Domain knowledge baked in** — Cycle architectures, key metrics (thermal/exergy efficiency, extraction ratio), property-data sources, and common methodological pitfalls (unclosed exergy balance, narrow working-fluid screening, missing baseline comparison) are written into the prompts. You don't re-teach it each time.
- **Data stays local** — Aside from the Claude calls and academic searches you initiate, nothing is uploaded. `workspace/` sits in your current directory — visible, editable, backup-friendly.
- **Cross-session memory** — Notes, drafts, and reviews are stored as markdown and keyword-searchable across sessions. It gets better the more you use it.
- **Reads PDFs itself** — Give it a local PDF or a DOI; it downloads, parses, deep-reads, and writes the notes.

## Who it's for

- Graduate students, PhDs, and early-career researchers in energy & power engineering and adjacent fields (renewables, nuclear, refrigeration/HVAC, thermal management, multi-energy systems)
- Anyone who often needs to *"quickly understand a new paper"*, *"turn a Chinese methods section into English for submission"*, or *"self-check before submission"*
- People comfortable with the command line, with their own API key (Anthropic direct, or a proxy's), who'd rather not paste drafts into web tools

> Not for: people who need a GUI, have no API key, or want the tool to pay its own API bill.

## Features

| Capability | What it does |
|---|---|
| 📚 Literature deep-read | Multi-source search + dedup + citation ranking; downloads OA PDFs; bilingual notes saved automatically |
| ✍️ Writing & polishing | ZH↔EN academic rewriting, target-journal style, point-by-point reviewer responses, batch rewriting of long docs |
| 🔍 Review / idea eval | Scores novelty / rigor / clarity / significance + line-level issues + major/minor revision list |
| 🧠 Domain knowledge | Energy/PE terminology, journal landscape, methodological pitfalls embedded in prompts |
| 🗂️ Cross-session notes | Keyword search across all markdown notes in `workspace/` |
| 🔌 Free data sources | OpenAlex / Crossref / Semantic Scholar / arXiv / Unpaywall — no keys |
| 🛡️ Write sandbox | File writes are confined to `workspace/` |

---

## Installation

Requires Python 3.11+ and an API key — Anthropic's for direct use, or your proxy's (see *Use a proxy* below).

### Option A: pipx (recommended, isolated)

```bash
pipx install git+https://github.com/1844514356zjc-dev/research-agent.git
```

This gives you a `research-agent` command. The `workspace/` folder is created in **whatever directory you run it from**.

### Option B: pip

```bash
pip install git+https://github.com/1844514356zjc-dev/research-agent.git
```

### Option C: from source (for development)

```bash
git clone https://github.com/1844514356zjc-dev/research-agent.git
cd research-agent
pip install -r requirements.txt
```

### Configure your API key

Create a `.env` in **the directory you'll run from** (or export env vars any way you like):

```bash
cp .env.example .env   # or create it
# Edit .env:
#   ANTHROPIC_API_KEY=sk-ant-...        (required — Anthropic's key, or your proxy's)
#   OUTPUT_LANG=en                       (optional: zh/en/ja/es/de; auto-detected if unset)
#   UNPAYWALL_EMAIL=you@your-school.edu  (optional, real email — helps find OA PDFs)
#   MODEL=claude-sonnet-5                (optional, override default model)
```

> `.env` is in `.gitignore` — it won't be committed.
>
> 💡 **Don't want to configure manually?** Just run `research-agent` — if no API key is found it launches a **first-run wizard** that walks you through key / output language / model, writes `.env` for you, and drops you into the REPL in ~30 seconds.

---

## Quick start (30 seconds)

```bash
cd ~/my-research        # any working directory
research-agent literature
```

Then just type your question:

```
你: Search highly-cited papers on the sCO2 Brayton cycle from the last 5 years,
    deep-read the most-cited one, and write notes in English.
```

It handles everything: multi-source search → dedup & rank → find an OA PDF → download & deep-read → generate bilingual notes in `workspace/notes/`. Streaming output, so you watch it call tools and read content live.

---

## Usage

Launch:

```bash
research-agent                       # pick a mode interactively
research-agent literature            # go straight to literature mode
research-agent writing --model opus  # writing mode + opus
research-agent review  --model opus  # review benefits from opus
```

> From source, replace `research-agent` with `python main.py`.

### Mode 1: Literature search & deep-read (`literature`)

The most-used mode. Example prompts:

- `Search for reviews on ORC working-fluid selection, last 5 years, highly cited`
- `What's DOI 10.1016/j.energy.2019.115900 about? Give me notes in English.`
- `Which R245fa-related papers have I read before?` (auto-searches local notes)

### Mode 2: Writing & polishing (`writing`)

- Paste a methods paragraph: `Rewrite this in Applied Energy style, preserving all numbers and units.`
- Paste reviewer comments: `Reply point-by-point, professional tone.`
- Batch-rewrite a long doc (see `/rewrite`).

### Mode 3: Review / idea evaluation (`review`)

- `/pdf ~/Downloads/manuscript.pdf`
- `Evaluate novelty and methodological rigor; give a major/minor list.`
- Output: four scores (1–5) + line-level issues + actionable fixes + overall verdict.

### Command reference

Inside the REPL, commands start with `/`:

| Command | Effect | Example |
|---|---|---|
| `/examples` | Show example prompts for the current mode | |
| `/pdf <path...>` | Preload one or more PDFs (glob supported) | `/pdf ~/Downloads/*.pdf` |
| `/rewrite <path> [--to en\|zh] [--style "..."]` | Batch-rewrite a md/txt file, section by section; saves with `-en`/`-zh` suffix | `/rewrite drafts/methods.md --to en --style "Applied Energy"` |
| `/notes [keywords]` | List notes; with keywords, full-text search | `/notes orc fluid` |
| `/mode <mode>` | Switch mode (clears history) | `/mode writing` |
| `/model <name>` | Switch model: `sonnet`/`opus`/`haiku` or full id | `/model opus` |
| `/lang <zh\|en\|ja\|es\|de>` | Switch output language (takes effect on next reply) | `/lang en` |
| `/usage` | Show this session's token usage | |
| `/status` | Show current state (mode/lang/model/workspace/msgs/usage) | |
| `/save <name>` | Save the conversation to `workspace/notes/` | `/save orc-survey` |
| `/clear` | Clear current history | |
| `/help` `/quit` | Help / quit | |

---

## Tools & data sources

The agent picks from these tools during a conversation (you can also ask for one by name):

**Search (all free, no key)**

| Tool | Source | Use |
|---|---|---|
| `search_papers` | OpenAlex / Crossref / Semantic Scholar / arXiv | Keyword search; `source="all"` dedupes & ranks by citations |
| `get_citations` | Semantic Scholar | "who cited this" or "this paper's references" |
| `get_open_pdf` | Unpaywall | Find a legal OA PDF URL by DOI |

**Local**

| Tool | Use |
|---|---|
| `read_pdf` | Extract text from a local PDF; supports `pages="1-5"` or `"2,4,6"` |
| `download_pdf` | Download a URL's PDF to `workspace/papers/` |
| `read_file` / `write_file` | Read/write local text (writes confined to `workspace/`) |
| `search_notes` / `list_notes` | Keyword search across notes / list all notes |

---

## Configuration

All config via environment variables (`.env` or shell):

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | Your API key (Anthropic's own key for direct use; the proxy's master key when using a proxy) |
| `ANTHROPIC_BASE_URL` | — | Use a proxy: the proxy's base URL (e.g. `http://localhost:4000` for LiteLLM). Unset = direct to Anthropic |
| `MODEL` | — | Default `claude-sonnet-5`; review benefits from `claude-opus-4-8`; when using a proxy, the model name the proxy knows |
| `OUTPUT_LANG` | — | Output language: `zh`/`en`/`ja`/`es`/`de`. Auto-detected from system locale if unset (default `zh`). Switch live with `/lang` |
| `UNPAYWALL_EMAIL` | — | Contact email for OA lookups — use a **real** address (`example.com` is rejected) |

**Model tips:** `sonnet` for everyday search/read/write (fast, cheap, good enough); switch to `opus` for deep reviews where reasoning matters (slower, pricier).

**Output language:** auto-detected from your system locale by default. Change it via the `OUTPUT_LANG` env var, the first-run wizard, or `/lang en` mid-session (takes effect on the next reply).

### Use a proxy (DeepSeek / Qwen / local models)

Don't want Anthropic? Run a LiteLLM proxy — it exposes the Anthropic `/v1/messages` protocol and translates to any backend. No code changes.

1. Install LiteLLM: `pip install 'litellm[proxy]'`
2. Write `litellm-config.yaml` (example running DeepSeek):
   ```yaml
   model_list:
     - model_name: deepseek-chat
       litellm_params:
         model: deepseek/deepseek-chat
         api_key: sk-your-deepseek-key
   # master_key: sk-proxy-anything   # optional: lock the proxy itself
   ```
3. Start it: `litellm --config litellm-config.yaml --port 4000`
4. Set your `.env`:
   ```bash
   ANTHROPIC_API_KEY=sk-proxy-anything      # the master_key above (anything if unset)
   ANTHROPIC_BASE_URL=http://localhost:4000
   MODEL=deepseek-chat                       # matches model_name in the config
   ```
5. Run `research-agent` as usual. `/status` will show "backend: proxy http://localhost:4000".

> Tool-calling is translated by the proxy; DeepSeek / Qwen / OpenAI-family all work reliably. Smaller or local models may be weaker at multi-turn tool use. To switch backend, just change `model:` in the config — zero code changes.

---

## Typical workflows

### ① Literature survey for a proposal

```bash
research-agent literature
你: Search "supercritical CO2 recompression Brayton cycle + solar" highly-cited papers from the last 5 years; dedup and give me the top 10.
你: Deep-read #1, #3, #7 and write notes for each.
你: Synthesize a research-gap analysis across them.
你: /save sco2-solar-survey
```

### ② Chinese methods → Applied Energy English

```bash
research-agent writing
你: /rewrite drafts/methods-zh.md --to en --style "Applied Energy"
```

Section-by-section "source point → rewrite" pairs; data/units/symbols/equation numbers preserved; output saved as `drafts/methods-zh-en.md`.

### ③ Pre-submission self-review

```bash
research-agent review --model opus
你: /pdf ~/Downloads/manuscript.pdf
你: Evaluate against Energy journal standards, focus on novelty and rigor, give a major/minor list.
你: /save self-review-v1
```

---

## Architecture

```mermaid
flowchart LR
  U([You / researcher]) --> REPL[/REPL · slash commands/]
  REPL --> Mode{Mode}
  Mode -->|literature| M1[Lit search & read]
  Mode -->|writing| M2[Write & polish]
  Mode -->|review| M3[Review & eval]
  M1 --> T[9 tools · streaming tool-calling]
  M2 --> T
  M3 --> T
  T -->|free academic APIs| API[(OpenAlex · Crossref<br/>Semantic Scholar · arXiv · Unpaywall)]
  T -->|local sandbox| WS[(workspace/<br/>notes · drafts · reviews · papers)]
  API --> Claude[(Claude API)]
  Claude --> Out[Notes / English draft / Review list]
```

## Illustrative session

<details>
<summary><b>▶ See what a literature deep-read looks like</b> (output illustrative, not a live screenshot)</summary>

```
Research Agent · Energy & Power Engineering
Mode: literature   Model: claude-sonnet-5   Workspace: /Users/me/my-research/workspace

你: Search highly-cited ORC working-fluid papers; deep-read the top one.

→ calling 1 tool: search_papers
Source: all (multi-source dedup, 3/4 sources responded) | Query: organic rankine cycle working fluid
5 results after dedup (ranked by citations)
1. Effect of working fluids on organic Rankine cycle for waste heat recovery (2004) [cited=761]
   DOI: 10.1016/j.energy.2004.01.004 ...
→ calling 2 tools: get_open_pdf, read_pdf

The most-cited is Liu & Chien (2004). Summary:
[Research question] How working-fluid choice affects ORC performance for low-grade waste-heat recovery …
[Method] Thermodynamic comparison of 11 fluids at identical boundary conditions …
[Key finding] R245fa gives the highest thermal efficiency (8.5%) at a 120°C source …
[Limitation] Thermal-stability ceiling not considered …
[Implication for your work] …

→ written to: workspace/notes/liu-2004-orc-working-fluids.md  (1.8KB)
```

</details>

---

## Project structure

```
research-agent/
├── main.py            # CLI entry + REPL + slash commands
├── agent.py           # streaming tool-calling loop
├── tools.py           # 9 tools + JSON schemas (search/local/notes)
├── prompts.py         # 3 mode prompts + energy/PE domain knowledge
├── test_offline.py    # offline deterministic tests (run by CI)
├── pyproject.toml     # packaging + research-agent entry point
├── requirements.txt
└── workspace/         # runtime output (gitignored), auto-created in cwd
    ├── notes/         # literature notes, conversation archives
    ├── drafts/        # writing/polishing output
    ├── reviews/       # review records
    └── papers/        # downloaded PDFs
```

---

## FAQ

**Does it need internet?** Yes. Search uses academic APIs; rewriting uses the Claude API. Reading a local PDF doesn't.

**How much does the API cost?** The main cost is Claude. A literature deep-read with Sonnet (including a few tool calls) is typically a few hundred to low-thousand tokens — a few cents. Opus is ~5–15× pricier; reserve it for deep reviews.

**I'm getting rate-limited (429)?** Semantic Scholar and OpenAlex throttle unauthenticated requests. `source="all"` skips failed sources and uses the rest; retry shortly. A real `UNPAYWALL_EMAIL` puts you in the polite pool.

**Can it read paywalled papers?** Only open-access full text. Non-OA papers still return metadata (title/authors/year/DOI/citations/abstract) but no PDF — copyright forbids it.

**Where are notes stored?** In `workspace/` under **the directory you run from**, as plain markdown. Run elsewhere → different workspace.

**Other disciplines?** Domain knowledge lives in `DOMAIN_KNOWLEDGE` in [`prompts.py`](prompts.py) — edit that block to repurpose it (chemistry, materials, mechanical…). The search/writing tools are discipline-agnostic.

**Can I change the output language?** Yes — three ways: set `OUTPUT_LANG` (`zh`/`en`/`ja`/`es`/`de`), pick it in the first-run wizard, or run `/lang en` mid-session (takes effect on the next reply). Unset → auto-detected from your system locale.

**The PDF text comes out empty?** It's probably a scanned PDF (image only, no text layer). The tool detects this and warns; run it through OCR first (`ocrmypdf`, Tesseract, Adobe Acrobat OCR) to add a text layer.

**How long is chat history kept?** In-memory for the current session only. `/save` archives it; the next launch is a fresh session — but `workspace/` notes persist.

---

## Limitations

- Requires an API key (direct Anthropic, or via proxy; billed per use, on you)
- Default output language is Chinese (ask it to switch, or edit `prompts.py`)
- Note search is keyword-based, not semantic/vector
- Only open-access full-text PDFs; non-OA papers return metadata only
- arXiv / Semantic Scholar occasionally flaky or rate-limited (handled gracefully)

---

## Contributing

Issues and PRs welcome. Small fixes: just send a PR. Larger changes: please open an issue first to discuss direction.

Run the tests:

```bash
python test_offline.py            # offline deterministic tests, no network/key
python -m py_compile *.py         # syntax check
```

CI runs a Python 3.11–3.14 matrix on every push.

---

## License

[MIT](LICENSE)
