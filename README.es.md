# Research Agent · Energy & Power Engineering

[简体中文](README.md) | [English](README.en.md) | [日本語](README.ja.md) | **Español** | [Deutsch](README.de.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![CI](https://github.com/1844514356zjc-dev/research-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/1844514356zjc-dev/research-agent/actions/workflows/ci.yml)

> **Un asistente de investigación en línea de comandos para ingeniería energética y de la potencia — lectura profunda de literatura, revisión académica, evaluación de manuscritos.**

Un asistente de investigación en consola para investigadores en **ingeniería energética y de la potencia**. Resuelve tres tareas cotidianas en una sola terminal: **búsqueda y lectura profunda de literatura, redacción y revisión de artículos, evaluación de manuscritos e ideas**. Los *prompts* del sistema incorporan conocimiento del dominio —ciclos Rankine/Brayton/combinados, ORC, sCO₂, HRSG, análisis de exergía— y el estilo de las revistas objetivo (Energy, Applied Energy, Applied Thermal Engineering, ECAM, ASME JEGTP).

Funciona con la API de Claude. La búsqueda bibliográfica se apoya totalmente en **APIs académicas gratuitas** (OpenAlex / Crossref / Semantic Scholar / arXiv / Unpaywall), sin claves adicionales. Tus notas, borradores y revisiones se guardan en una carpeta local `workspace/`; no se sube nada a terceros.

> 🌐 **Nota de idioma:** El agente **responde por defecto en chino** (con términos técnicos en inglés). Responderá en español (o cualquier idioma) si simplemente se lo pides —p. ej., *"responde en español"*. Para cambiar el predeterminado de forma permanente, edita el *prompt* en [`prompts.py`](prompts.py).
>
> 📝 Las traducciones de este README pueden ir por detrás del [original en chino (README.md)](README.md), que es la versión de referencia.

---

## Por qué usarlo

Hay muchas herramientas de investigación con IA; esta toma algunas decisiones distintas:

- **Coste de búsqueda cero** — Sin búsqueda de pago; ni siquiera usa el `web_search` de Anthropic. Las APIs académicas son más precisas, más académicas y totalmente gratuitas.
- **Desduplicación multi-fuente** — `source="all"` fusiona resultados de OpenAlex + Crossref + Semantic Scholar + arXiv, desduplica por DOI + título y ordena por citas. Sin limpieza manual; sin sesgo de una sola base de datos.
- **Conocimiento del dominio integrado** — Arquitecturas de ciclos, métricas clave (eficiencia térmica/exergética, fracción de extracción), fuentes de propiedades termodinámicas y trampas metodológicas habituales (balance de exergía que no cierra, selección estrecha de fluidos de trabajo, falta de caso base de comparación) están escritos en los *prompts*. No tienes que enseñárselo cada vez.
- **Datos locales** — Salvo las llamadas a Claude y las búsquedas académicas que tú inicias, no se sube nada. `workspace/` está en tu directorio actual: visible, editable, fácil de respaldar.
- **Memoria entre sesiones** — Notas, borradores y revisiones se guardan como markdown y se pueden buscar por palabras clave entre sesiones. Cuanto más lo usas, más útil es.
- **Lee PDFs por sí mismo** — Dale un PDF local o un DOI; lo descarga, analiza, lee en profundidad y redacta las notas.

## Para quién es

- Estudiantes de posgrado, doctorandos e investigadores jóvenes en ingeniería energética y de la potencia, y áreas afines (renovables, nuclear, refrigeración y HVAC, gestión térmica, sistemas multienergéticos)
- Quien necesite a menudo *"entender rápido un artículo nuevo"*, *"pasar una sección de Métodos del chino al inglés para envío"*, o *"revisión propia antes de enviar"*
- Personas cómodas con la línea de comandos, con su propia clave API de Anthropic, que prefieren no pegar borradores en herramientas web

> No es para: quien necesite interfaz gráfica, no tenga clave API de Anthropic, o espere que la herramienta pague su propia factura de API.

## Funcionalidades

| Capacidad | Qué hace |
|---|---|
| 📚 Lectura profunda de literatura | Búsqueda multi-fuente + desduplicación + ranking por citas; descarga PDFs OA; notas bilingües guardadas automáticamente |
| ✍️ Redacción y revisión | Reescritura académica ZH↔EN, estilo de la revista objetivo, respuestas *point-by-point* a revisores, reescritura por lotes de documentos largos |
| 🔍 Revisión / evaluación de ideas | Puntúa novedad / rigor / claridad / significancia + problemas a nivel de línea + lista major/minor |
| 🧠 Conocimiento del dominio | Terminología de energía/potencia, revistas y trampas metodológicas integradas en los *prompts* |
| 🗂️ Notas entre sesiones | Búsqueda por palabras clave en todas las notas markdown de `workspace/` |
| 🔌 Fuentes de datos gratuitas | OpenAlex / Crossref / Semantic Scholar / arXiv / Unpaywall — sin claves |
| 🛡️ Sandbox de escritura | La escritura de archivos se limita a `workspace/` |

---

## Instalación

Necesitas Python 3.11+ y una [clave API de Anthropic](https://console.anthropic.com).

### Opción A: pipx (recomendado, aislado)

```bash
pipx install git+https://github.com/1844514356zjc-dev/research-agent.git
```

Te queda el comando `research-agent`. La carpeta `workspace/` se crea en **el directorio desde donde lo ejecutes**.

### Opción B: pip

```bash
pip install git+https://github.com/1844514356zjc-dev/research-agent.git
```

### Opción C: desde fuente (para desarrollo)

```bash
git clone https://github.com/1844514356zjc-dev/research-agent.git
cd research-agent
pip install -r requirements.txt
```

### Configura tu clave API

Crea un `.env` en **el directorio desde donde ejecutarás** (o exporta las variables como prefieras):

```bash
cp .env.example .env   # o créalo
# Edita .env:
#   ANTHROPIC_API_KEY=sk-ant-...        (obligatorio, https://console.anthropic.com)
#   UNPAYWALL_EMAIL=you@your-school.edu  (opcional, correo real — mejora la búsqueda de PDFs OA)
#   MODEL=claude-sonnet-5                (opcional, sobreescribe el modelo por defecto)
```

> `.env` está en `.gitignore` — no se confirma al repositorio.

---

## Inicio rápido (30 segundos)

```bash
cd ~/mi-investigacion     # cualquier directorio de trabajo
research-agent literature
```

Luego solo escribe tu pregunta:

```
你: Busca artículos muy citados del ciclo Brayton de sCO2 de los últimos 5 años;
    lee en profundidad el más citado y redacta las notas en español.
```

Se encarga de todo: búsqueda multi-fuente → desduplicar y ordenar → buscar un PDF OA → descargar y leer → generar notas bilingües en `workspace/notes/`. La salida es en *streaming*, así que ves en vivo cómo llama a las herramientas y lee el contenido.

---

## Uso

Arranque:

```bash
research-agent                       # elegir modo interactivamente
research-agent literature            # ir directo al modo literatura
research-agent writing --model opus  # modo redacción + opus
research-agent review  --model opus  # revisión se beneficia de opus
```

> Desde fuente, sustituye `research-agent` por `python main.py`.

### Modo 1: Búsqueda y lectura profunda de literatura (`literature`)

El modo más usado. Ejemplos:

- `Busca revisiones sobre selección de fluidos de trabajo en ORC, últimos 5 años, muy citadas`
- `¿De qué trata el DOI 10.1016/j.energy.2019.115900? Dame las notas en español.`
- `¿Qué artículos relacionados con R245fa he leído antes?` (busca en las notas locales)

### Modo 2: Redacción y revisión (`writing`)

- Pega un párrafo de métodos: `Reescríbalo al estilo de Applied Energy, conservando todos los números y unidades.`
- Pega comentarios de revisores: `Responde punto por punto, tono profesional.`
- Reescritura por lotes (ver `/rewrite`).

### Modo 3: Revisión / evaluación de ideas (`review`)

- `/pdf ~/Downloads/manuscript.pdf`
- `Evalúa novedad y rigor metodológico; entrega una lista major/minor.`
- Salida: cuatro puntajes (1–5) + problemas a nivel de línea + correcciones accionables + veredicto global.

### Referencia de comandos

Dentro del REPL, los comandos empiezan con `/`:

| Comando | Efecto | Ejemplo |
|---|---|---|
| `/pdf <ruta...>` | Precarga uno o más PDFs (admite *glob*) | `/pdf ~/Downloads/*.pdf` |
| `/rewrite <ruta> [--to en\|zh] [--style "..."]` | Reescritura por lotes sección por sección; guarda con sufijo `-en`/`-zh` | `/rewrite drafts/methods.md --to en --style "Applied Energy"` |
| `/notes [palabras]` | Lista notas; con palabras, búsqueda de texto completo | `/notes orc fluido` |
| `/mode <modo>` | Cambia de modo (borra el historial) | `/mode writing` |
| `/model <nombre>` | Cambia de modelo: `sonnet`/`opus`/`haiku` o id completo | `/model opus` |
| `/save <nombre>` | Guarda la conversación en `workspace/notes/` | `/save orc-survey` |
| `/clear` | Borra el historial actual | |
| `/help` `/quit` | Ayuda / salir | |

---

## Herramientas y fuentes de datos

El agente elige entre estas herramientas durante la conversación (puedes pedir una por nombre):

**Búsqueda (todas gratuitas, sin clave)**

| Herramienta | Fuente | Uso |
|---|---|---|
| `search_papers` | OpenAlex / Crossref / Semantic Scholar / arXiv | Búsqueda por palabras clave; `source="all"` desduplica y ordena por citas |
| `get_citations` | Semantic Scholar | "quién citó esto" o "referencias de este artículo" |
| `get_open_pdf` | Unpaywall | URL de un PDF OA legal por DOI |

**Locales**

| Herramienta | Uso |
|---|---|
| `read_pdf` | Extrae texto de un PDF local; admite `pages="1-5"` o `"2,4,6"` |
| `download_pdf` | Descarga el PDF de una URL a `workspace/papers/` |
| `read_file` / `write_file` | Lee/escribe texto local (escritura limitada a `workspace/`) |
| `search_notes` / `list_notes` | Búsqueda por palabras clave / listar todas las notas |

---

## Configuración

Toda la configuración va por variables de entorno (`.env` o *shell*):

| Variable | Obligatoria | Descripción |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | Tu clave API de Claude |
| `MODEL` | — | Por defecto `claude-sonnet-5`; revisión se beneficia de `claude-opus-4-8` |
| `UNPAYWALL_EMAIL` | — | Correo de contacto para OA — usa uno **real** (`example.com` se rechaza) |

**Consejos de modelo:** `sonnet` para búsqueda/lectura/escritura diaria (rápido, barato, suficiente); cambia a `opus` para revisiones profundas donde importa el razonamiento (más lento y caro).

---

## Flujos de trabajo típicos

### ① Revisión de literatura para una propuesta

```bash
research-agent literature
你: Busca artículos muy citados de "ciclo Brayton de recompresión de CO2 supercrítico + solar"
    de los últimos 5 años; desduplica y dame el top 10.
你: Lee en profundidad #1, #3, #7 y redacta notas de cada uno.
你: Sintetiza un análisis de vacíos de investigación entre ellos.
你: /save sco2-solar-survey
```

### ② Métodos en chino → Applied Energy en inglés

```bash
research-agent writing
你: /rewrite drafts/methods-zh.md --to en --style "Applied Energy"
```

Pares "punto del original → reescritura" sección por sección; se conservan datos/unidades/símbolos/números de ecuación; salida en `drafts/methods-zh-en.md`.

### ③ Auto-revisión antes del envío

```bash
research-agent review --model opus
你: /pdf ~/Downloads/manuscript.pdf
你: Evalúa según estándares de la revista Energy, centrarse en novedad y rigor, lista major/minor.
你: /save self-review-v1
```

---

## Sesión ilustrativa

Así se ve una lectura profunda de literatura (salida ilustrativa, no es captura en vivo):

```
Research Agent · Energy & Power Engineering
Mode: literature   Model: claude-sonnet-5   Workspace: /Users/me/mi-investigacion/workspace

你: Busca artículos muy citados sobre fluidos de trabajo en ORC; lee el primero.

→ calling 1 tool: search_papers
Source: all (multi-source dedup, 3/4 sources responded) | Query: organic rankine cycle working fluid
5 results after dedup (ranked by citations)
1. Effect of working fluids on organic Rankine cycle for waste heat recovery (2004) [cited=761]
   DOI: 10.1016/j.energy.2004.01.004 ...
→ calling 2 tools: get_open_pdf, read_pdf

El más citado es Liu & Chien (2004). Resumen:
[Pregunta de investigación] Cómo afecta la elección de fluido de trabajo al rendimiento del ORC …
[Método] Comparación termodinámica de 11 fluidos en idénticas condiciones …
[Hallazgo clave] R245fa alcanza la mayor eficiencia térmica (8.5%) con fuente a 120°C …
[Limitación] No se considera el techo de estabilidad térmica …
[Implicación] …

→ written to: workspace/notes/liu-2004-orc-working-fluids.md  (1.8KB)
```

---

## Estructura del proyecto

```
research-agent/
├── main.py            # entrada CLI + REPL + comandos slash
├── agent.py           # bucle de tool-calling en streaming
├── tools.py           # 9 herramientas + esquemas JSON (búsqueda/local/notas)
├── prompts.py         # prompts de los 3 modos + conocimiento del dominio
├── test_offline.py    # pruebas deterministas sin red (las ejecuta CI)
├── pyproject.toml     # empaquetado + entry point research-agent
├── requirements.txt
└── workspace/         # salida en runtime (gitignore), se crea en cwd
    ├── notes/         # notas de literatura, archivos de conversación
    ├── drafts/        # salida de redacción/revisión
    ├── reviews/       # registros de revisión
    └── papers/        # PDFs descargados
```

---

## Preguntas frecuentes

**¿Necesita internet?** Sí. La búsqueda usa APIs académicas; la reescritura usa la API de Claude. Leer un PDF local, no.

**¿Cuánto cuesta la API?** El coste principal es Claude. Una lectura profunda con Sonnet (incluidas varias llamadas a herramientas) suele ser de unos cientos a miles de tokens: unos céntimos. Opus es ~5–15× más caro; resérvalo para revisiones profundas.

**¿Me limitan (429)?** Semantic Scholar y OpenAlex limitan peticiones sin clave. `source="all"` omite fuentes fallidas y usa las demás; reintenta en breve. Un `UNPAYWALL_EMAIL` real te pone en el *polite pool*.

**¿Lee artículos de pago?** Solo textos completos en acceso abierto. Los no-OA devuelven metadatos (título/autores/año/DOI/citas/resumen) pero no PDF —por derechos.

**¿Dónde se guardan las notas?** En `workspace/` bajo **el directorio desde donde ejecutas**, en markdown plano. Ejecútalo en otro sitio → otro *workspace*.

**¿Otras disciplinas?** El conocimiento del dominio está en `DOMAIN_KNOWLEDGE` en [`prompts.py`](prompts.py) —edita ese bloque para adaptarlo (química, materiales, mecánica…). Las herramientas de búsqueda/escritura son agnósticas a la disciplina.

**¿Cuánto se guarda el historial?** Solo en memoria, en la sesión actual. `/save` lo archiva; el próximo arranque es sesión nueva, pero las notas en `workspace/` persisten.

---

## Limitaciones conocidas

- Requiere clave API de Anthropic (uso facturado, a tu cargo)
- El idioma por defecto es chino (pídele cambiarlo o edita `prompts.py`)
- La búsqueda de notas es por palabras clave, no semántica/vectorial
- Solo PDFs de texto completo en acceso abierto; los no-OA devuelven solo metadatos
- arXiv / Semantic Scholar a veces son inestables o se limitan (manejado con degradación elegante)

---

## Contribuir

Issues y PR bienvenidos. Arreglos pequeños: manda un PR directamente. Cambios grandes: abre primero un issue para discutir la dirección.

Ejecutar las pruebas:

```bash
python test_offline.py            # pruebas deterministas sin red/clave
python -m py_compile *.py         # comprobación de sintaxis
```

CI ejecuta una matriz Python 3.11–3.14 en cada *push*.

---

## Licencia

[MIT](LICENSE)
