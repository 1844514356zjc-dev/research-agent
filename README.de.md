# Research Agent · Energy & Power Engineering

[简体中文](README.md) | [English](README.en.md) | [日本語](README.ja.md) | [Español](README.es.md) | **Deutsch**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![CI](https://github.com/1844514356zjc-dev/research-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/1844514356zjc-dev/research-agent/actions/workflows/ci.yml)

> **Ein CLI-Forschungsassistent für Energie- und Antriebstechnik — Literatur-Tiefenlektüre, akademisches Polishing, Manuskript-Begutachtung.**

Ein Kommandozeilen-Forschungsassistent für Forschende im Bereich **Energie- und Antriebstechnik**. Drei Alltagsaufgaben in einem Terminal: **Literatursuche und -tieferlesen, Schreiben und Polieren von Arbeiten, Begutachtung und Ideenbewertung**. Die System-Prompts enthalten Domänenwissen — Rankine-/Brayton-/Kombikreisprozesse, ORC, sCO₂, HRSG (Abhitzedampferzeuger), Exergie-Analyse — und den Schreibstil der Zieljournale (Energy, Applied Energy, Applied Thermal Engineering, ECAM, ASME JEGTP).

Angetrieben von der Claude-API. Die Literatursuche läuft vollständig über **kostenlose akademische APIs** (OpenAlex / Crossref / Semantic Scholar / arXiv / Unpaywall) — keine zusätzlichen API-Schlüssel nötig. Notizen, Entwürfe und Gutachten bleiben in einem lokalen Ordner `workspace/`; es wird nichts hochgeladen.

> 🌐 **Hinweis zur Sprache:** Der Agent **antwortet standardmäßig auf Chinesisch** (mit englischen Fachbegriffen). Er antwortet auf Deutsch (oder jeder anderen Sprache), wenn du ihn einfach darum bittest — z. B. *"antworte auf Deutsch"*. Um den Standard dauerhaft zu ändern, bearbeite den Prompt in [`prompts.py`](prompts.py).
>
> 📝 Übersetzungen dieser README können hinter dem [chinesischen Original (README.md)](README.md) als maßgeblicher Version hinterherhinken.

---

## Warum dieses Tool

Es gibt viele KI-Forschungstools; dieses trifft ein paar andere Entscheidungen:

- **Null Suchkosten** — Keine bezahlte Suche; nicht einmal Anthropics eigenes `web_search` wird verwendet. Akademische APIs sind präziser, wissenschaftlicher und komplett kostenlos.
- **Multi-Quellen-Dedup** — `source="all"` führt Ergebnisse aus OpenAlex + Crossref + Semantic Scholar + arXiv zusammen, dedupliziert nach DOI + Titel und sortiert nach Zitaten. Kein manuelles Bereinigen; kein Ein-Quellen-Bias.
- **Eingebettetes Domänenwissen** — Kreisarchitekturen, Kennzahlen (thermischer/exergetischer Wirkungsgrad, Entnahmedampf-Anteil), Stoffdatenquellen und häufige methodische Fallstricke (nicht geschlossene Exergiebilanz, enge Arbeitsstoff-Auswahl, fehlender Basisfall-Vergleich) stehen in den Prompts. Du musst sie nicht jedes Mal neu beibringen.
- **Daten bleiben lokal** — Außer den Claude-Aufrufen und akademischen Suchen, die du selbst auslöst, wird nichts hochgeladen. `workspace/` liegt in deinem aktuellen Verzeichnis — sichtbar, bearbeitbar, einfach zu sichern.
- **Sitzungsübergreifendes Gedächtnis** — Notizen, Entwürfe und Gutachten werden als Markdown gespeichert und sind sitzungsübergreifend per Stichwort durchsuchbar. Je mehr du nutzt, desto nützlicher.
- **Liest PDFs selbst** — Gib ein lokales PDF oder eine DOI an; es lädt herunter, parst, liest tief und erstellt Notizen.

## Für wen

- Masterstudierende, Doktoranden und Nachwuchsforschende in Energie- und Antriebstechnik sowie Nachbarfeldern (Erneuerbare, Kerntechnik, Kältetechnik/HVAC, Thermomanagement, Multivektorsysteme)
- Wer oft *"ein neues Papier schnell verstehen"*, *"einen chinesischen Methodenabschnitt ins Englische für die Einreichung bringen"* oder *"vor der Einreichung selbst prüfen"* muss
- Menschen, die mit der Kommandozeile vertraut sind, einen eigenen Anthropic-API-Schlüssel haben und ihre Entwürfe lieber nicht in Web-Tools einfügen

> Nicht geeignet für: Personen, die eine GUI brauchen, keinen Anthropic-API-Schlüssel haben oder erwarten, dass das Tool seine API-Rechnung selbst trägt.

## Funktionen

| Fähigkeit | Beschreibung |
|---|---|
| 📚 Literatur-Tiefenlektüre | Multi-Quellen-Suche + Dedup + Zitats-Ranking; lädt OA-PDFs herunter; speichert automatisch zweisprachige Notizen |
| ✍️ Schreiben & Polieren | Akademisches Umschreiben ZH↔EN, Stil der Zieljournale, *point-by-point*-Antworten auf Gutachten, Stapel-Umschreiben langer Dokumente |
| 🔍 Begutachtung / Ideenbewertung | Bewertet Neuheit / Stringenz / Klarheit / Signifikanz + zeilenweise Probleme + Major/Minor-Liste |
| 🧠 Domänenwissen | Terminologie, Journal-Landschaft und methodische Fallstricke der Energie-/Antriebstechnik in Prompts eingebettet |
| 🗂️ Sitzungsübergreifende Notizen | Stichwortsuche über alle Markdown-Notizen in `workspace/` |
| 🔌 Kostenlose Datenquellen | OpenAlex / Crossref / Semantic Scholar / arXiv / Unpaywall — ohne Schlüssel |
| 🛡️ Schreib-Sandbox | Dateischreiben ist auf `workspace/` beschränkt |

---

## Installation

Benötigt Python 3.11+ und einen [Anthropic-API-Schlüssel](https://console.anthropic.com).

### Option A: pipx (empfohlen, isoliert)

```bash
pipx install git+https://github.com/1844514356zjc-dev/research-agent.git
```

Stellt den Befehl `research-agent` bereit. Der Ordner `workspace/` wird **im Verzeichnis erstellt, aus dem du startest**.

### Option B: pip

```bash
pip install git+https://github.com/1844514356zjc-dev/research-agent.git
```

### Option C: aus dem Source (für Entwicklung)

```bash
git clone https://github.com/1844514356zjc-dev/research-agent.git
cd research-agent
pip install -r requirements.txt
```

### API-Schlüssel einrichten

Lege eine `.env` **im Ausführungsverzeichnis** an (oder exportiere die Variablen beliebig):

```bash
cp .env.example .env   # oder neu anlegen
# .env bearbeiten:
#   ANTHROPIC_API_KEY=sk-ant-...        (erforderlich, https://console.anthropic.com)
#   UNPAYWALL_EMAIL=you@your-school.edu  (optional, echte Adresse — verbessert OA-PDF-Suche)
#   MODEL=claude-sonnet-5                (optional, überschreibt Standardmodell)
```

> `.env` steht in `.gitignore` — wird nicht committet.

---

## Schnellstart (30 Sekunden)

```bash
cd ~/meine-forschung       # beliebiges Arbeitsverzeichnis
research-agent literature
```

Dann einfach die Frage eintippen:

```
你: Suche stark zitierte Arbeiten zum sCO2-Brayton-Kreisprozess der letzten 5 Jahre;
    lies die am häufigsten zitierte tief und erstelle Notizen auf Deutsch.
```

Übernimmt alles: Multi-Quellen-Suche → Dedup & Rang → OA-PDF finden → herunterladen & tieflesen → zweisprachige Notizen in `workspace/notes/`. Streaming-Ausgabe, du siehst live, welche Tools aufgerufen werden und was gelesen wird.

---

## Nutzung

Start:

```bash
research-agent                       # Modus interaktiv wählen
research-agent literature            # direkt in den Literatur-Modus
research-agent writing --model opus  # Schreib-Modus + opus
research-agent review  --model opus  # Begutachtung profitiert von opus
```

> Aus dem Source ersetze `research-agent` durch `python main.py`.

### Modus 1: Literatursuche & Tiefenlesen (`literature`)

Der am häufigsten genutzte Modus. Beispiele:

- `Suche Reviews zur Auswahl von Arbeitsstoffen im ORC, letzte 5 Jahre, stark zitiert`
- `Worum geht es bei DOI 10.1016/j.energy.2019.115900? Notizen auf Deutsch.`
- `Welche R245fa-bezogenen Papiere habe ich schon gelesen?` (durchsucht lokale Notizen)

### Modus 2: Schreiben & Polieren (`writing`)

- Methodenabschnitt einfügen: `Schreibe dies im Stil von Applied Energy um, alle Zahlen und Einheiten erhalten.`
- Gutachterkommentare einfügen: `Antworte Punkt für Punkt, professioneller Ton.`
- Stapel-Umschreiben (siehe `/rewrite`).

### Modus 3: Begutachtung / Ideenbewertung (`review`)

- `/pdf ~/Downloads/manuscript.pdf`
- `Bewerte Neuheit und methodische Stringenz; erstelle eine Major/Minor-Liste.`
- Ausgabe: vier Scores (1–5) + zeilenweise Probleme + umsetzbare Vorschläge + Gesamturteil.

### Befehlsreferenz

Im REPL beginnen Befehle mit `/`:

| Befehl | Wirkung | Beispiel |
|---|---|---|
| `/pdf <pfad...>` | Eine oder mehrere PDFs vorladen (Glob unterstützt) | `/pdf ~/Downloads/*.pdf` |
| `/rewrite <pfad> [--to en\|zh] [--style "..."]` | Stapelweises Umschreiben abschnittsweise; speichert mit `-en`/`-zh`-Suffix | `/rewrite drafts/methods.md --to en --style "Applied Energy"` |
| `/notes [stichworte]` | Notizen auflisten; mit Stichworten Volltextsuche | `/notes orc fluid` |
| `/mode <modus>` | Modus wechseln (löscht Verlauf) | `/mode writing` |
| `/model <name>` | Modell wechseln: `sonnet`/`opus`/`haiku` oder vollständige ID | `/model opus` |
| `/save <name>` | Konversation in `workspace/notes/` speichern | `/save orc-survey` |
| `/clear` | Aktuellen Verlauf löschen | |
| `/help` `/quit` | Hilfe / Beenden | |

---

## Werkzeuge und Datenquellen

Der Agent wählt während der Konversation aus diesen Werkzeugen (du kannst sie auch namentlich verlangen):

**Suche (alles kostenlos, ohne Schlüssel)**

| Werkzeug | Quelle | Nutzung |
|---|---|---|
| `search_papers` | OpenAlex / Crossref / Semantic Scholar / arXiv | Stichwortsuche; `source="all"` dedupliziert & sortiert nach Zitaten |
| `get_citations` | Semantic Scholar | "wer hat das zitiert" oder "Referenzen dieser Arbeit" |
| `get_open_pdf` | Unpaywall | Legale OA-PDF-URL per DOI finden |

**Lokal**

| Werkzeug | Nutzung |
|---|---|
| `read_pdf` | Text aus lokalem PDF extrahieren; unterstützt `pages="1-5"` oder `"2,4,6"` |
| `download_pdf` | PDF einer URL nach `workspace/papers/` laden |
| `read_file` / `write_file` | Lokale Texte lesen/schreiben (Schreiben auf `workspace/` beschränkt) |
| `search_notes` / `list_notes` | Stichwortsuche über Notizen / alle Notizen auflisten |

---

## Konfiguration

Alle Einstellungen über Umgebungsvariablen (`.env` oder Shell):

| Variable | Erforderlich | Beschreibung |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | Dein Claude-API-Schlüssel |
| `MODEL` | — | Standard `claude-sonnet-5`; Begutachtung profitiert von `claude-opus-4-8` |
| `UNPAYWALL_EMAIL` | — | Kontakt-E-Mail für OA-Suche — **echte** Adresse verwenden (`example.com` wird abgelehnt) |

**Modell-Tipps:** `sonnet` für alltägliche Suche/Lesen/Schreiben (schnell, günstig, ausreichend); wechsle für tiefe Begutachtungen zu `opus` (langsamer, teurer, aber tiefer).

---

## Typische Workflows

### ① Literaturübersicht für einen Antrag

```bash
research-agent literature
你: Suche stark zitierte Arbeiten zu "supercritical CO2 recompression Brayton cycle + solar"
    der letzten 5 Jahre; dedupliziere und gib mir die Top 10.
你: Lies #1, #3, #7 tief und erstelle jeweils Notizen.
你: Synthese eine Forschungslücken-Analyse über alle.
你: /save sco2-solar-survey
```

### ② Chinesischer Methodenabschnitt → Applied Energy Englisch

```bash
research-agent writing
你: /rewrite drafts/methods-zh.md --to en --style "Applied Energy"
```

Abschnittsweise "Quellpunkt → Umschreibung"-Paare; Daten/Einheiten/Symbole/Gleichungsnummern bleiben erhalten; Ausgabe als `drafts/methods-zh-en.md`.

### ③ Selbst-Begutachtung vor der Einreichung

```bash
research-agent review --model opus
你: /pdf ~/Downloads/manuscript.pdf
你: Bewerte nach Standards der Zeitschrift Energy, Fokus auf Neuheit und Stringenz, Major/Minor-Liste.
你: /save self-review-v1
```

---

## Illustrative Sitzung

So sieht ein Literatur-Tiefenlesen aus (Ausgabe illustrativ, kein Live-Screenshot):

```
Research Agent · Energy & Power Engineering
Mode: literature   Model: claude-sonnet-5   Workspace: /Users/me/meine-forschung/workspace

你: Suche stark zitierte ORC-Arbeiten zu Arbeitsstoffen; lies die oberste.

→ calling 1 tool: search_papers
Source: all (multi-source dedup, 3/4 sources responded) | Query: organic rankine cycle working fluid
5 results after dedup (ranked by citations)
1. Effect of working fluids on organic Rankine cycle for waste heat recovery (2004) [cited=761]
   DOI: 10.1016/j.energy.2004.01.004 ...
→ calling 2 tools: get_open_pdf, read_pdf

Am häufigsten zitiert: Liu & Chien (2004). Zusammenfassung:
[Fragestellung] Wie die Wahl des Arbeitsstoffs die ORC-Leistung beeinflusst …
[Methode] Thermodynamischer Vergleich von 11 Fluiden unter gleichen Randbedingungen …
[Zentrales Ergebnis] R245fa erreicht den höchsten thermischen Wirkungsgrad (8,5 %) bei 120 °C Quelle …
[Einschränkung] Thermische Stabilitätsgrenze nicht berücksichtigt …
[Implikation] …

→ written to: workspace/notes/liu-2004-orc-working-fluids.md  (1.8KB)
```

---

## Projektstruktur

```
research-agent/
├── main.py            # CLI-Einstieg + REPL + Slash-Befehle
├── agent.py           # Streaming-Tool-Calling-Schleife
├── tools.py           # 9 Werkzeuge + JSON-Schemas (Suche/Lokal/Notizen)
├── prompts.py         # 3 Modus-Prompts + Energie-/Antriebs-Domänenwissen
├── test_offline.py    # deterministische Offline-Tests (von CI ausgeführt)
├── pyproject.toml     # Packaging + research-Agent-Einstieg
├── requirements.txt
└── workspace/         # Laufzeitausgabe (gitignore), wird in cwd angelegt
    ├── notes/         # Literatur-Notizen, Konversationsarchive
    ├── drafts/        # Schreib-/Polier-Ausgaben
    ├── reviews/       # Gutachten-Protokolle
    └── papers/        # heruntergeladene PDFs
```

---

## FAQ

**Braucht es Internet?** Ja. Suche nutzt akademische APIs; Umschreiben die Claude-API. Ein lokales PDF zu lesen, braucht keins.

**Was kostet die API?** Die Hauptkosten sind Claude. Ein Tiefenlesen mit Sonnet (inkl. weniger Tool-Aufrufe) kostet typischerweise wenige hundert bis wenige tausend Token — einige Cent. Opus ist ~5–15× teurer; für tiefe Begutachtungen reservieren.

**Ich werde gedrosselt (429)?** Semantic Scholar und OpenAlex drosseln unauthentifizierte Anfragen. `source="all"` überspringt fehlerhafte Quellen und nutzt den Rest; kurz später erneut versuchen. Eine echte `UNPAYWALL_EMAIL` bringt dich in den *polite pool*.

**Kann es Bezahlpapiere lesen?** Nur Open-Access-Volltexte. Nicht-OA liefern Metadaten (Titel/Autoren/Jahr/DOI/Zitate/Abstract), aber kein PDF — urheberrechtliche Beschränkung.

**Wo liegen die Notizen?** In `workspace/` unter **dem Verzeichnis, aus dem du startest**, als klares Markdown. Woanders gestartet → anderes Workspace.

**Andere Disziplinen?** Das Domänenwissen steht in `DOMAIN_KNOWLEDGE` in [`prompts.py`](prompts.py) — diesen Block anpassen (Chemie, Werkstoffe, Maschinenbau …). Die Such-/Schreib-Werkzeuge sind disziplinagnostisch.

**Wie lange bleibt der Verlauf?** Nur im Speicher der aktuellen Sitzung. `/save` archiviert; der nächste Start ist eine neue Sitzung — aber die Notizen in `workspace/` bleiben.

---

## Bekannte Einschränkungen

- Benötigt Anthropic-API-Schlüssel (abrechnungspflichtige Nutzung, zu deinen Lasten)
- Standard-Ausgabesprache ist Chinesisch (zum Wechseln auffordern oder `prompts.py` ändern)
- Notizsuche ist stichwortbasiert, nicht semantisch/vektoriell
- Nur OA-Volltext-PDFs; Nicht-OA nur Metadaten
- arXiv / Semantic Scholar gelegentlich instabil oder gedrosselt (werden elegant abgefangen)

---

## Beitragen

Issues und PRs willkommen. Kleine Fixes: direkt PR senden. Größere Änderungen: bitte vorher ein Issue zur Richtung eröffnen.

Tests ausführen:

```bash
python test_offline.py            # deterministische Offline-Tests, ohne Netz/Schlüssel
python -m py_compile *.py         # Syntaxprüfung
```

CI führt bei jedem Push eine Matrix für Python 3.11–3.14 aus.

---

## Lizenz

[MIT](LICENSE)
