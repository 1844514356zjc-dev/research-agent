# 科研实用 Agent（能源/动力工程）

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![CI](https://github.com/1844514356zjc-dev/research-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/1844514356zjc-dev/research-agent/actions/workflows/ci.yml)

一个独立运行的 Python 命令行科研助手，覆盖三类日常任务：

- **文献检索与精读** — OpenAlex / Semantic Scholar / Crossref / arXiv 检索（免费、无需 key），开放获取 PDF 下载，双语对照笔记
- **论文写作与润色** — 中英文学术改写、目标期刊风格适配、审稿意见 point-by-point 回复
- **审稿 / 思路评估** — 创新/严谨/清晰/意义四维打分 + 行级问题 + 修改清单

底层用 Claude（默认 `claude-sonnet-5`，审稿可切 `claude-opus-4-8`）。

## 安装

```bash
cd ~/research-agent
python3 -m venv .venv && source .venv/bin/activate   # 可选但推荐
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 ANTHROPIC_API_KEY（https://console.anthropic.com）
# （可选）填 UNPAYWALL_EMAIL 为你的真实邮箱，找 OA PDF 更顺
```

## 使用

```bash
python main.py                       # 交互式选模式
python main.py literature            # 直入文献模式
python main.py writing --model opus  # 写作模式 + opus
python main.py review  --model opus  # 审稿推荐用 opus
```

### 对话中的命令

| 命令 | 作用 |
|---|---|
| `/pdf <路径...>` | 预载一篇或多篇 PDF（支持通配符），如 `/pdf ~/Downloads/*.pdf` |
| `/rewrite <路径> [--to en\|zh] [--style "..."]` | 批量改写一个 md/txt 文件：逐节翻译/润色并存新文件（`-en`/`-zh` 后缀） |
| `/notes [关键词]` | 列出已有笔记；给关键词则跨笔记全文检索（跨会话回查） |
| `/mode literature\|writing\|review` | 切模式（清空历史） |
| `/model sonnet\|opus\|haiku` | 切模型 |
| `/save <名>` | 把当前对话存到 `workspace/notes/` |
| `/clear` | 清空当前模式历史 |
| `/help` `/quit` | 帮助 / 退出 |

### 典型场景

**1. 多源检索 + 去重 + 精读**
```
你: 检索近 5 年 sCO₂ 布雷顿循环高被引论文，精读最高引用那篇并出中文笔记
```
Agent 会用 `search_papers(source="all")` 把 OpenAlex/Crossref/S2/arXiv 结果按 DOI+标题去重合并、按引用数排序，再 `get_open_pdf` → `download_pdf` → `read_pdf` → `write_file`。

**2. 批量改写长文**
```
你: /mode writing
你: /rewrite drafts/methods-zh.md --to en --style "Applied Energy"
```
Agent 逐节（按 `##` 标题）给"原文要点→改写"对照，保留数据/单位/公式编号，成品存为 `methods-zh-en.md`。

**3. 跨会话回查既往笔记**
```
你: /notes orc 工质          # 直接看命中段落
或
你: 之前读过哪些 R245fa 相关的？   # Agent 自动调 search_notes
```

**4. 审稿多篇对比**
```
你: /mode review
你: /pdf ~/Downloads/a.pdf ~/Downloads/b.pdf
你: 对比这两篇的创新性与方法严谨性
```

## 项目结构

```
main.py        CLI + REPL
agent.py       流式 tool-calling 循环
tools.py       7 个工具实现 + schema（检索/本地）
prompts.py     三模式系统提示词 + 能源/动力工程领域知识
workspace/     运行时输出：notes/ drafts/ reviews/ papers/（已 gitignore）
```

## 检索源说明（均免费、无需 key）

| 源 | 用途 | 特点 |
|---|---|---|
| **OpenAlex**（默认） | 通用文献 | 引用数、开放获取链接、覆盖广 |
| **Semantic Scholar** | 引用图 | `get_citations` 查被引/参考文献 |
| **Crossref** | DOI 元数据 | 权威书目信息 |
| **arXiv** | 预印本 | 免费 PDF |
| **Unpaywall** | 找 OA PDF | 经 DOI 查合法免费全文 |

## 备注

- 不集成 Anthropic 付费 web_search；学术 API 更精准、零成本。
- 工具返回有字符截断（默认 12000），长 PDF 用 `pages` 参数分段读。
- 写入仅限 `workspace/` 下，避免误伤外部文件。
