"""离线确定性测试（无网络、无 API key）— 给 CI 用，也可本地跑：python test_offline.py

只测纯逻辑：去重、规范化、笔记检索、文件读写沙箱、命令行参数解析。
不触网、不调 Claude API。
"""

import os
import shlex
import sys

import tools


def test_normalize_doi():
    assert tools._normalize_doi("https://doi.org/10.1/A ") == "10.1/a"
    assert tools._normalize_doi("DOI:10.1/x") == "10.1/x"
    assert tools._normalize_doi(None) is None
    assert tools._normalize_doi("") is None


def test_normalize_title():
    assert tools._normalize_title("ORC, Cycle!") == "orc cycle"
    assert tools._normalize_title("  Supercritical  CO₂ ") == "supercritical co"


def test_dedupe_merges_by_title_when_one_lacks_doi():
    recs = [
        {"title": "ORC for Waste Heat", "doi": "10.1/a", "cited_by_count": 100, "source": "openalex"},
        {"title": "orc for waste heat!", "doi": None, "cited_by_count": 80, "source": "crossref"},
        {"title": "Another Paper", "doi": "10.1/b", "cited_by_count": 50, "source": "openalex"},
    ]
    # 两种顺序都应合并成 2 条
    for order in (recs, list(reversed(recs))):
        d = tools._dedupe(order)
        assert len(d) == 2, f"期望 2 条，实际 {len(d)}"
        assert any(r.get("sources") == "crossref+openalex" for r in d), "应有合并自两源的记录"
        # 引用数取最大
        merged = next(r for r in d if tools._normalize_doi(r.get("doi")) == "10.1/a")
        assert merged["cited_by_count"] == 100


def test_dedupe_same_doi_different_title_merges():
    recs = [
        {"title": "Title One", "doi": "10.1/x", "cited_by_count": 10, "source": "openalex"},
        {"title": "Totally Different", "doi": "10.1/x", "cited_by_count": 20, "source": "crossref"},
    ]
    d = tools._dedupe(recs)
    assert len(d) == 1, f"同 DOI 应合并: {len(d)}"
    assert d[0]["cited_by_count"] == 20


def test_notes_search_and_list():
    tools.write_file("notes/_test_.md",
                     "# ORC Test\n\n有机朗肯循环（ORC）工质筛选，R245fa 最佳。\n\n## 方法\n采用㶲分析。")
    try:
        r = tools.search_notes("orc 工质")
        assert "R245fa" in r and "匹配 2 词" in r, f"应命中且计分 2: {r[:120]}"
        # 无匹配
        nm = tools.search_notes("不存在的词zzz")
        assert "无匹配" in nm
        # 列表
        lst = tools.list_notes()
        assert "_test_" in lst
    finally:
        os.remove(str(tools.WORKSPACE / "notes" / "_test_.md"))


def test_write_read_roundtrip():
    tools.write_file("notes/_wr_.md", "hello world")
    try:
        assert "hello world" in tools.read_file("notes/_wr_.md")
    finally:
        os.remove(str(tools.WORKSPACE / "notes" / "_wr_.md"))


def test_write_sandbox_blocks_escape():
    # workspace 之外的绝对路径应被拒
    r = tools.write_file("/tmp/_escape_attempt_.md", "x")
    assert "拒绝" in r, f"应拒绝 workspace 外写入: {r}"
    assert not os.path.exists("/tmp/_escape_attempt_.md")


def test_rewrite_arg_parsing():
    # 复刻 main.do_rewrite 的 shlex 解析逻辑
    toks = shlex.split('drafts/m.md --to en --style "Applied Energy"')
    assert toks[0] == "drafts/m.md"
    to, style, i = "en", "", 1
    while i < len(toks):
        if toks[i] == "--to" and i + 1 < len(toks):
            to = toks[i + 1]; i += 2
        elif toks[i] == "--style" and i + 1 < len(toks):
            style = toks[i + 1]; i += 2
        else:
            i += 1
    assert to == "en" and style == "Applied Energy"


def test_prompts_system_for_all_modes_and_langs():
    import prompts
    for mode in prompts.MODES:
        s = prompts.system_for(mode)
        assert isinstance(s, str) and len(s) > 200, f"{mode} 提示词过短"
        assert "当前模式" in s, f"{mode} 缺少模式标记"
        for lang in prompts.SUPPORTED_LANGS:
            s = prompts.system_for(mode, lang)
            assert isinstance(s, str) and len(s) > 200, f"{mode}/{lang} 过短"
    # 无效模式应抛错
    try:
        prompts.system_for("nope"); assert False, "应抛 ValueError"
    except ValueError:
        pass


def test_prompts_examples_present():
    import prompts
    for mode in prompts.MODES:
        for lang in prompts.SUPPORTED_LANGS:
            ex = prompts.examples_for(mode, lang)
            assert ex and len(ex) >= 2, f"{mode}/{lang} 缺示例"


def test_lang_detection_returns_supported():
    import prompts
    assert prompts._detect_lang.__call__  # 可调用
    # OUTPUT_LANG 优先
    import os
    old = os.environ.get("OUTPUT_LANG")
    try:
        os.environ["OUTPUT_LANG"] = "ja"
        assert prompts._detect_lang() == "ja"
        os.environ["OUTPUT_LANG"] = "es"
        assert prompts._detect_lang() == "es"
        os.environ.pop("OUTPUT_LANG", None)
        # 无 OUTPUT_LANG 时也应返回受支持代码（默认 zh 或系统语言）
        assert prompts._detect_lang() in prompts.SUPPORTED_LANGS
    finally:
        if old is not None:
            os.environ["OUTPUT_LANG"] = old
        else:
            os.environ.pop("OUTPUT_LANG", None)


def test_agent_base_url_passthrough():
    """走代理：ResearchAgent 应把 ANTHROPIC_BASE_URL 透传给客户端（构造离线，不联网）。"""
    import os
    saved = {k: os.environ.get(k) for k in
             ("ANTHROPIC_API_KEY", "ANTHROPIC_BASE_URL", "MODEL")}
    try:
        os.environ["ANTHROPIC_API_KEY"] = "dummy-key"
        os.environ["ANTHROPIC_BASE_URL"] = "http://localhost:4000"
        os.environ["MODEL"] = "deepseek-chat"
        import agent as _agent
        ag = _agent.ResearchAgent(mode="literature")
        assert ag.base_url == "http://localhost:4000", "base_url 应被记录"
        assert ag.model == "deepseek-chat", "MODEL 应透传"
        # SDK 客户端应指向代理（不联网，仅检查配置）
        client_url = str(getattr(ag.client, "base_url", "") or "")
        assert "localhost:4000" in client_url, f"客户端 base_url 应含代理地址: {client_url}"
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_agent_direct_when_no_base_url():
    """不设 ANTHROPIC_BASE_URL 时 base_url 为空（直连 Anthropic）。"""
    import os
    saved = {k: os.environ.get(k) for k in
             ("ANTHROPIC_API_KEY", "ANTHROPIC_BASE_URL")}
    try:
        os.environ["ANTHROPIC_API_KEY"] = "dummy-key"
        os.environ.pop("ANTHROPIC_BASE_URL", None)
        import agent as _agent
        ag = _agent.ResearchAgent(mode="review")
        assert ag.base_url == ""
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_bibtex_key_and_format():
    import tools
    work = {
        "DOI": "10.1016/j.energy.2004.01.004",
        "title": ["Effect of working fluids on organic Rankine cycle for waste heat recovery"],
        "container-title": ["Energy"],
        "published": {"date-parts": [[2004]]},
        "volume": "29", "issue": "8", "page": "1207-1217",
        "author": [{"family": "Liu", "given": "Bo-Tau"},
                   {"family": "Chien", "given": "Kuo-Hsiang"}],
    }
    key = tools._bibtex_key(work)
    assert key == "liu2004effect", f"key={key}"
    bib = tools._format_bibtex(key, work)
    assert "@article{liu2004effect," in bib
    assert "Liu, Bo-Tau and Chien, Kuo-Hsiang" in bib   # 作者 and 分隔
    assert "1207--1217" in bib                          # 单横杠 → 双横杠
    assert "10.1016/j.energy.2004.01.004" in bib
    assert "{2004}" in bib
    assert "{Energy}" in bib


def test_bibtex_key_missing_fields():
    import tools
    # 无作者、无年、标题前几个词全为冠词/介词
    work = {"title": ["On the Theory of Everything"], "DOI": "10.x/y"}
    key = tools._bibtex_key(work)
    assert key == "anonndtheory", f"key={key}"   # anon + nd + 首个实义词 theory


def test_export_bibtex_rejects_empty():
    import tools
    assert "需要非空" in tools.export_bibtex([])
    assert "需要非空" in tools.export_bibtex("not-a-list")  # 非列表


def _run_all():
    tests = [(k, v) for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  ✓ {name}")
        except AssertionError as e:
            failed += 1
            print(f"  ✗ {name}: {e}")
        except Exception as e:
            failed += 1
            print(f"  ✗ {name}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if _run_all() else 0)
