"""工具实现 + JSON schema。

检索类（免费、无需 API key）：OpenAlex / Crossref / Semantic Scholar / arXiv / Unpaywall。
本地类：read_pdf / read_file / write_file / download_pdf。

新增检索源只需：写一个 _search_xxx(query, n) 函数，并在 search_papers 里加分支。
"""

import os
import re
import json
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

WORKSPACE = Path(__file__).resolve().parent / "workspace"
WORKSPACE.mkdir(exist_ok=True)
for sub in ("notes", "drafts", "reviews", "papers"):
    (WORKSPACE / sub).mkdir(exist_ok=True)

EMAIL = os.getenv("UNPAYWALL_EMAIL") or "research-agent@users.noreply.github.com"
HEADERS = {"User-Agent": f"research-agent/0.1 (mailto:{EMAIL})"}

_MAX_CHARS = 12000  # 单个工具返回的字符上限，防止撑爆上下文


def _truncate(s: str, limit: int = _MAX_CHARS) -> str:
    if len(s) <= limit:
        return s
    return s[:limit] + f"\n…[已截断，共 {len(s)} 字符]"


def _oa_abstract_from_inverted(inv: dict) -> str:
    """OpenAlex 的 abstract_inverted_index 是倒排索引，重建为正文。"""
    if not inv:
        return ""
    positions = []
    for word, idxs in inv.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(w for _, w in positions)


def _normalize_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    d = doi.strip().lower()
    for pfx in ("https://doi.org/", "http://dx.doi.org/", "doi:"):
        if d.startswith(pfx):
            d = d[len(pfx):]
    return d.strip() or None


def _normalize_title(title: str | None) -> str:
    if not title:
        return ""
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def _dedupe(records: list[dict]) -> list[dict]:
    """按 DOI 优先、其次规范化标题去重；合并字段、取引用数最大值。
    用 DOI 与标题两个索引互相匹配，避免"一源有 DOI 一源无 DOI"时漏合。"""
    merged: list[dict] = []
    by_doi: dict[str, dict] = {}
    by_title: dict[str, dict] = {}
    for r in records:
        doi = _normalize_doi(r.get("doi"))
        title_n = _normalize_title(r.get("title"))
        target = None
        if doi and doi in by_doi:
            target = by_doi[doi]
        elif title_n and title_n in by_title:
            target = by_title[title_n]
        if target is None:
            r["_src"] = {r.get("source")} - {None}
            merged.append(r)
            if doi:
                by_doi[doi] = r
            if title_n:
                by_title[title_n] = r
        else:
            for k, v in r.items():
                if not target.get(k) and v:
                    target[k] = v
            cc = r.get("cited_by_count")
            if cc:
                target["cited_by_count"] = max(target.get("cited_by_count") or 0, cc)
            if r.get("source"):
                target["_src"].add(r["source"])
            if doi and not _normalize_doi(target.get("doi")):
                by_doi[doi] = target
    for r in merged:
        r["sources"] = "+".join(sorted(s for s in r["_src"] if s))
        r.pop("_src", None)
    return merged


# ---------------------------------------------------------------------------
# 检索源
# ---------------------------------------------------------------------------

def _search_openalex(query: str, n: int) -> list[dict]:
    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per-page": min(max(n, 1), 25),
        "mailto": EMAIL,        # 进 polite pool，限额更高
        "tool": "research-agent",
    }
    r = requests.get(url, params=params, headers=HEADERS, timeout=20)
    r.raise_for_status()
    out = []
    for w in r.json().get("results", [])[:n]:
        authors = ", ".join(
            a["author"]["display_name"]
            for a in (w.get("authorships") or [])[:3]
        ) + (" 等" if len(w.get("authorships") or []) > 3 else "")
        oa = w.get("open_access") or {}
        out.append({
            "title": w.get("title") or w.get("display_name") or "?",
            "authors": authors,
            "year": (w.get("publication_year")),
            "doi": (w.get("doi") or "").replace("https://doi.org/", "") or None,
            "cited_by_count": w.get("cited_by_count", 0),
            "abstract": _oa_abstract_from_inverted(w.get("abstract_inverted_index")),
            "oa_url": oa.get("oa_url"),
            "venue": w.get("host_venue", {}).get("display_name") if isinstance(w.get("host_venue"), dict) else None,
            "source": "openalex",
        })
    return out


def _search_crossref(query: str, n: int) -> list[dict]:
    url = "https://api.crossref.org/works"
    params = {"query": query, "rows": min(max(n, 1), 25)}
    r = requests.get(url, params=params, headers=HEADERS, timeout=20)
    r.raise_for_status()
    out = []
    for it in r.json()["message"].get("items", [])[:n]:
        authors = ", ".join(
            f"{a.get('given','')} {a.get('family','')}".strip()
            for a in (it.get("author") or [])[:3]
        )
        dp = (it.get("published") or {}).get("date-parts", [[None]])[0]
        year = dp[0] if dp else None
        out.append({
            "title": (it.get("title") or ["?"])[0],
            "authors": authors,
            "year": year,
            "doi": it.get("DOI"),
            "cited_by_count": it.get("is-referenced-by-count", 0),
            "abstract": _strip_jats(it.get("abstract")),
            "venue": (it.get("container-title") or [None])[0],
            "oa_url": None,
            "source": "crossref",
        })
    return out


def _search_semanticscholar(query: str, n: int) -> list[dict]:
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": min(max(n, 1), 25),
        "fields": "title,year,authors,citationCount,abstract,openAccessPdf,externalIds,venue",
    }
    r = requests.get(url, params=params, headers=HEADERS, timeout=25)
    r.raise_for_status()
    out = []
    for p in r.json().get("data", [])[:n]:
        authors = ", ".join(a.get("name", "") for a in (p.get("authors") or [])[:3])
        oa = p.get("openAccessPdf") or {}
        ext = p.get("externalIds") or {}
        out.append({
            "title": p.get("title") or "?",
            "authors": authors,
            "year": p.get("year"),
            "doi": ext.get("DOI"),
            "cited_by_count": p.get("citationCount", 0),
            "abstract": p.get("abstract"),
            "oa_url": oa.get("url"),
            "venue": p.get("venue"),
            "source": "semanticscholar",
        })
    return out


def _search_arxiv(query: str, n: int) -> list[dict]:
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "max_results": min(max(n, 1), 25),
        "sortBy": "relevance",
    }
    r = requests.get(url, params=params, headers=HEADERS, timeout=25)
    r.raise_for_status()
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(r.text)
    out = []
    for e in root.findall("a:entry", ns):
        title = (e.findtext("a:title", default="", namespaces=ns) or "").strip()
        summary = (e.findtext("a:summary", default="", namespaces=ns) or "").strip()
        idurl = (e.findtext("a:id", default="", namespaces=ns) or "")
        arxiv_id = idurl.rsplit("/", 1)[-1]
        published = (e.findtext("a:published", default="", namespaces=ns) or "")[:4]
        authors = ", ".join(
            (e.findtext("a:name", default="", namespaces=ns) or "")
            for e in e.findall("a:author", ns)
        )[:120]
        pdf = next(
            (l.get("href") for l in e.findall("a:link", ns)
             if l.get("title") == "pdf"),
            None,
        )
        out.append({
            "title": " ".join(title.split()),
            "authors": authors,
            "year": int(published) if published.isdigit() else None,
            "doi": None,
            "cited_by_count": None,
            "abstract": " ".join(summary.split()),
            "oa_url": pdf,
            "venue": f"arXiv:{arxiv_id}",
            "source": "arxiv",
        })
    return out


def _strip_jats(xml: str | None) -> str | None:
    """Crossref 摘要常是 JATS XML，剥成纯文本。"""
    if not xml:
        return None
    try:
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", xml)).strip()
    except Exception:
        return xml


_SEARCHERS = {
    "openalex": _search_openalex,
    "crossref": _search_crossref,
    "semanticscholar": _search_semanticscholar,
    "arxiv": _search_arxiv,
}


def search_papers(query: str, n: int = 5, source: str = "openalex") -> str:
    """检索论文。source='all' 并发查 OpenAlex/Crossref/S2/arXiv 并按 DOI+标题去重合并，
    按引用数排序。其余单源按原行为。"""
    if source == "all":
        records: list[dict] = []
        ok, fail = [], []
        for src_name, fn in _SEARCHERS.items():
            try:
                records.extend(fn(query, n))
                ok.append(src_name)
            except requests.RequestException:
                fail.append(src_name)  # 单源失败不影响整体
        results = _dedupe(records)
        results.sort(key=lambda r: -(r.get("cited_by_count") or 0))
        results = results[:n]
        coverage = f"响应 {len(ok)}/{len(_SEARCHERS)} 源" + (f"（{'+'.join(fail)} 限流或失败）" if fail else "")
        header = (f"来源: all（多源去重合并，{coverage}）| 查询: {query} | "
                  f"去重后 {len(results)} 条（按引用数排序）\n")
    else:
        fn = _SEARCHERS.get(source, _search_openalex)
        try:
            results = fn(query, n)
        except requests.RequestException as e:
            return f"[{source} 检索失败: {e}]"
        header = f"来源: {source} | 查询: {query} | 命中 {len(results)} 条（按相关性）\n"
    if not results:
        return f"[{source} 无结果: query={query!r}]"
    lines = [header]
    for i, r in enumerate(results, 1):
        cited = r.get("cited_by_count")
        cited_s = str(cited) if cited is not None else "?"
        lines.append(
            f"{i}. {r['title']} ({r.get('year') or '?'})  [cited={cited_s}]"
        )
        if r.get("authors"):
            lines.append(f"   作者: {r['authors']}")
        if r.get("venue"):
            lines.append(f"   期刊: {r['venue']}")
        if r.get("doi"):
            lines.append(f"   DOI: {r['doi']}")
        if r.get("oa_url"):
            lines.append(f"   OA: {r['oa_url']}")
        if r.get("sources"):
            lines.append(f"   合并自: {r['sources']}")
        if r.get("abstract"):
            ab = r["abstract"]
            lines.append("   摘要: " + ab[:400] + ("…" if len(ab) > 400 else ""))
        lines.append("")
    return _truncate("\n".join(lines))


def get_citations(doi_or_id: str, direction: str = "citing") -> str:
    """经 Semantic Scholar 取引用图：references（本文引用了谁）或 citing（谁引用了本文）。"""
    field, label = {
        "citing": ("citations", "被引（谁引用了本文）"),
        "references": ("references", "参考文献（本文引用了谁）"),
    }.get(direction, ("citations", "被引"))
    pid = doi_or_id if doi_or_id.lower().startswith("doi:") else f"DOI:{doi_or_id}"
    url = f"https://api.semanticscholar.org/graph/v1/paper/{pid}/{field}"
    params = {"fields": "title,year,authors,citationCount,externalIds", "limit": 20}
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=25)
        r.raise_for_status()
    except requests.RequestException as e:
        msg = str(e)[:80]
        hint = "（S2 对无 key 请求严格限流，稍后重试，或改用 OpenAlex 检索）" if "429" in msg else ""
        return f"[引用图查询失败: {msg} {hint}]"
    items = [
        (x.get("citingPaper") or x.get("referencedPaper"))
        for x in r.json().get(field, [])
    ]
    items = [x for x in items if x and (x.get("title"))]
    if not items:
        return f"[{label}: 无结果 for {doi_or_id}]"
    lines = [f"{label}（{len(items)} 条）for {doi_or_id}:\n"]
    for i, p in enumerate(items, 1):
        authors = ", ".join(a.get("name", "") for a in (p.get("authors") or [])[:2])
        ext = p.get("externalIds") or {}
        lines.append(
            f"{i}. {p.get('title','?')} ({p.get('year') or '?'})"
            f"  [cited={p.get('citationCount')}]"
        )
        if authors:
            lines.append(f"   作者: {authors}")
        if ext.get("DOI"):
            lines.append(f"   DOI: {ext['DOI']}")
    return _truncate("\n".join(lines))


def get_open_pdf(doi: str) -> str:
    """经 Unpaywall 查询 DOI 的合法开放获取 PDF 链接。"""
    doi = doi.strip()
    url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}"
    try:
        r = requests.get(url, params={"email": EMAIL}, headers=HEADERS, timeout=20)
        r.raise_for_status()
    except requests.RequestException as e:
        msg = str(e)[:80]
        if "404" in msg or "422" in msg:
            return f"[Unpaywall 无此 DOI 记录: {doi}。可尝试作者主页/ResearchGate/机构仓库。]"
        return f"[Unpaywall 查询失败: {msg}]"
    data = r.json()
    best = data.get("best_oa_location") or {}
    pdf = best.get("url_for_pdf") or best.get("url")
    title = data.get("title") or "?"
    is_oa = data.get("is_oa")
    journal = data.get("journal_name")
    lines = [f"标题: {title}", f"DOI: {doi}"]
    if journal:
        lines.append(f"期刊: {journal}")
    lines.append(f"开放获取: {'是' if is_oa else '否'}")
    if pdf:
        lines.append(f"PDF 链接: {pdf}")
        lines.append("(可用 download_pdf 下载，再 read_pdf 精读)")
    else:
        lines.append("未找到合法 OA PDF。可尝试作者主页/ResearchGate/机构仓库。")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 本地工具
# ---------------------------------------------------------------------------

def _resolve(path: str) -> Path:
    """允许 workspace 内任意路径，也允许任意已存在的绝对/相对路径（读）。
    写入限制在 workspace/ 下，见 write_file。"""
    p = Path(path).expanduser()
    if not p.is_absolute():
        p = (WORKSPACE / path)
    return p


def read_pdf(path: str, pages: str | None = None) -> str:
    """读取本地 PDF 文本。pages 可选 '1-5' 或 '1,3,5'。"""
    import pdfplumber  # 延迟导入，启动更快

    p = _resolve(path)
    if not p.exists():
        return f"[文件不存在: {p}]"
    page_idx = _parse_pages(pages)
    text_parts = []
    try:
        with pdfplumber.open(str(p)) as pdf:
            total = len(pdf.pages)
            targets = page_idx if page_idx is not None else range(total)
            for i in targets:
                if 0 <= i < total:
                    t = pdf.pages[i].extract_text() or ""
                    text_parts.append(f"--- 第 {i+1} 页 ---\n{t}")
            if not text_parts:
                return f"[PDF {total} 页，但指定页码无效]"
    except Exception as e:
        return f"[读取 PDF 失败: {e}]"
    return _truncate("\n\n".join(text_parts) + f"\n\n[共 {total} 页]")


def _parse_pages(spec: str | None) -> list[int] | None:
    if not spec:
        return None
    out = []
    for part in str(spec).split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a) - 1, int(b)))
        elif part.isdigit():
            out.append(int(part) - 1)
    return out


def read_file(path: str) -> str:
    p = _resolve(path)
    if not p.exists():
        return f"[文件不存在: {p}]"
    try:
        return _truncate(p.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return f"[读取失败: {e}]"


def write_file(path: str, content: str) -> str:
    """写入 workspace/ 下的文件（notes/drafts/reviews/…）。返回写入路径。"""
    p = Path(path).expanduser()
    if not p.is_absolute():
        p = WORKSPACE / path
    # 安全：禁止写到 workspace 之外
    try:
        p.resolve().relative_to(WORKSPACE.resolve())
    except ValueError:
        return f"[拒绝：写入仅限 workspace/ 下，你给的是 {p}]"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"[已写入: {p}  ({len(content)} 字符)]"


def download_pdf(url: str, dest: str | None = None) -> str:
    """下载 PDF（或任意文件）到 workspace/papers/。dest 为文件名或相对 workspace 的路径。"""
    if not dest:
        name = url.rsplit("/", 1)[-1].split("?")[0] or "paper.pdf"
        if not name.lower().endswith(".pdf"):
            name += ".pdf"
        dest = f"papers/{name}"
    p = Path(dest).expanduser()
    if not p.is_absolute():
        p = WORKSPACE / dest
    try:
        p.resolve().relative_to(WORKSPACE.resolve())
    except ValueError:
        return f"[拒绝：写入仅限 workspace/ 下]"
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        with requests.get(url, headers=HEADERS, timeout=60, stream=True) as r:
            r.raise_for_status()
            with open(p, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
        size_kb = p.stat().st_size / 1024
        return f"[已下载: {p}  ({size_kb:.0f} KB)，可用 read_pdf 读取]"
    except Exception as e:
        return f"[下载失败: {e}]"


# ---------------------------------------------------------------------------
# 跨会话笔记检索
# ---------------------------------------------------------------------------

def list_notes() -> str:
    """列出 workspace 下 notes/drafts/reviews 里的 markdown 文件。"""
    lines = []
    for sub in ("notes", "drafts", "reviews"):
        d = WORKSPACE / sub
        files = sorted(d.glob("*.md"))
        if not files:
            continue
        lines.append(f"【{sub}】({len(files)} 篇)")
        for f in files:
            kb = f.stat().st_size / 1024
            lines.append(f"  {f.name}  ({kb:.0f} KB)")
    return "\n".join(lines) if lines else "[工作区暂无笔记]"


def search_notes(query: str, n: int = 5, scope: str = "all") -> str:
    """在 workspace 下已存的笔记/草稿/审稿里做关键词检索，按段落返回命中。"""
    terms = [t.lower().strip() for t in re.split(r"[,，\s]+", query) if t.strip()]
    if not terms:
        return list_notes()
    scopes = {
        "all": ["notes", "drafts", "reviews"],
        "notes": ["notes"], "drafts": ["drafts"], "reviews": ["reviews"],
    }.get(scope, ["notes", "drafts", "reviews"])
    hits = []  # (score, para_len, path, para_idx, para)
    for sub in scopes:
        for f in (WORKSPACE / sub).glob("*.md"):
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for pi, para in enumerate(re.split(r"\n\s*\n", text)):
                low = para.lower()
                score = sum(1 for t in terms if t in low)
                if score:
                    hits.append((score, len(para), f, pi + 1, para.strip()))
    hits.sort(key=lambda x: (-x[0], x[1]))
    if not hits:
        return f"[无匹配: {query}（检索范围 {scope}）]"
    lines = [f"笔记检索 '{query}' — 命中 {len(hits)} 段，显示前 {min(n, len(hits))}（范围 {scope}）\n"]
    for score, _, f, pi, para in hits[:n]:
        rel = f.relative_to(WORKSPACE)
        lines.append(f"### {rel} · 第 {pi} 段 · 匹配 {score} 词")
        lines.append(para[:500] + ("…" if len(para) > 500 else ""))
        lines.append("")
    return _truncate("\n".join(lines))


# ---------------------------------------------------------------------------
# Schema + 分发
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "search_papers",
        "description": "检索学术论文。默认 OpenAlex（含引用数、开放获取链接）。"
                       "源可选 openalex/crossref/semanticscholar/arxiv；选 'all' 会多源去重合并、按引用数排序（最全）。"
                       "想找之前读过的笔记用 search_notes。",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "检索关键词（中英文均可，建议英文）"},
                "n": {"type": "integer", "description": "返回条数，默认 5", "default": 5},
                "source": {
                    "type": "string",
                    "enum": ["all", "openalex", "crossref", "semanticscholar", "arxiv"],
                    "default": "openalex",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_citations",
        "description": "查引用关系：citing=谁引用了本文；references=本文的参考文献。需 DOI。",
        "input_schema": {
            "type": "object",
            "properties": {
                "doi": {"type": "string", "description": "DOI（如 10.1016/j.energy.2023.xxx）"},
                "direction": {
                    "type": "string",
                    "enum": ["citing", "references"],
                    "default": "citing",
                },
            },
            "required": ["doi"],
        },
    },
    {
        "name": "get_open_pdf",
        "description": "经 Unpaywall 查 DOI 的合法开放获取 PDF 链接。",
        "input_schema": {
            "type": "object",
            "properties": {"doi": {"type": "string"}},
            "required": ["doi"],
        },
    },
    {
        "name": "read_pdf",
        "description": "读取本地 PDF 文本。path 可为绝对路径或相对 workspace 的路径。"
                       "pages 可选如 '1-5' 或 '1,3,5'。",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "pages": {"type": "string", "description": "可选，如 '1-5' 或 '2,4,6'"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "read_file",
        "description": "读取本地文本/markdown 文件。",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "把内容写入 workspace/ 下的文件（notes/drafts/reviews/…）。"
                       "path 相对 workspace，如 'notes/wang-2023-orc.md'。",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "download_pdf",
        "description": "下载 URL 指向的 PDF 到 workspace/papers/。dest 可选，默认从 URL 推导文件名。",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "dest": {"type": "string", "description": "相对 workspace 的目标路径，如 'papers/x.pdf'"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "search_notes",
        "description": "在 workspace 下已存的 notes/drafts/reviews markdown 里做关键词检索，"
                       "按段落返回命中（跨会话回查既往笔记/草稿/审稿用）。"
                       "scope 可选 all/notes/drafts/reviews，默认 all。",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "关键词，空格/逗号分隔的多词按 AND 计分"},
                "n": {"type": "integer", "description": "返回段数，默认 5", "default": 5},
                "scope": {
                    "type": "string",
                    "enum": ["all", "notes", "drafts", "reviews"],
                    "default": "all",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "list_notes",
        "description": "列出 workspace 下 notes/drafts/reviews 里的全部 markdown 文件名与大小。",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]

_DISPATCH = {
    "search_papers": search_papers,
    "get_citations": get_citations,
    "get_open_pdf": get_open_pdf,
    "read_pdf": read_pdf,
    "read_file": read_file,
    "write_file": write_file,
    "download_pdf": download_pdf,
    "search_notes": search_notes,
    "list_notes": list_notes,
}


def dispatch(name: str, args: dict) -> str:
    fn = _DISPATCH.get(name)
    if fn is None:
        return f"[未知工具: {name}]"
    try:
        return str(fn(**(args or {})))
    except TypeError as e:
        return f"[参数错误 {name}: {e}]"
    except Exception as e:
        import traceback
        return f"[工具 {name} 执行失败: {e}\n{traceback.format_exc()[-400:]}]"


if __name__ == "__main__":
    # 离线自检：直接调用各检索源
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "supercritical CO2 Brayton cycle"
    print("=" * 30, "all（去重合并）", "=" * 30)
    print(search_papers(q, n=4, source="all"))
    print("=" * 30, "openalex", "=" * 30)
    print(search_papers(q, n=3, source="openalex"))
