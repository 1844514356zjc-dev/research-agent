# 科研实用 Agent · Energy & Power Engineering

**简体中文** | [English](README.en.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Deutsch](README.de.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![CI](https://github.com/1844514356zjc-dev/research-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/1844514356zjc-dev/research-agent/actions/workflows/ci.yml)

> **A CLI research assistant for energy & power engineering — literature deep-read, academic polishing, manuscript review.**

面向**能源/动力工程**研究者的命令行科研助手。在一个终端里完成**文献检索精读、论文写作润色、审稿与思路评估**三件日常事。默认中文交流、术语保留英文，系统提示词里内置了朗肯/布雷顿/联合循环、ORC、sCO₂、HRSG、㶲分析等本领域术语与目标期刊（Energy、Applied Energy、Applied Thermal Engineering、ECAM、ASME JEGTP）的写作风格。

底层是 Claude API；检索全走**免费学术 API**（OpenAlex / Crossref / Semantic Scholar / arXiv / Unpaywall），不需要任何额外 API key。你的笔记、草稿、审稿都存在本地 `workspace/`，不上传任何第三方。

---

## 为什么用它

市面上不缺 AI 科研工具，但这个有几个不一样的取舍：

- **零检索成本**　不依赖任何付费搜索；连 Anthropic 自家的 web_search 都没用——学术 API 更精准、更学术、完全免费。
- **多源去重**　一句 `source="all"`，把 OpenAlex + Crossref + Semantic Scholar + arXiv 的结果按 DOI+标题去重合并、按引用数排序。你不用再手动剔重，也不会被某一家库的偏差带偏。
- **领域知识内嵌**　提示词里写进了循环构型、关键指标（热效率、㶲效率、抽汽率）、物性数据来源、常见方法论陷阱（㶲平衡不闭合、工质筛选范围过窄、基准工况对比缺失……），不必每次都重新教它。
- **数据留在本机**　除了你主动发起的 Claude 调用与学术检索，没有上传；`workspace/` 就在你当前目录下，随时可看、可改、可备份。
- **跨会话积累**　检索过的文献、改写过的稿件、做过的审稿，都按 markdown 落盘，可随时用关键词跨笔记回查——做得越久越好用。
- **能自己读 PDF**　给一个本地 PDF 或 DOI，它自己下载、解析、精读、出笔记。

## 适合谁

- 能源/动力工程，以及相邻方向（可再生能源、核能、制冷与空调、热管理、多能互补）的研究生、博士生、青年研究者
- 经常要做"快速看懂一篇新论文""把中文方法段改成英文投稿""投稿前自查"的人
- 习惯命令行、有自己的 Anthropic API key、不想把稿子和数据塞进网页工具的人

> 不适合：需要图形界面、没有 Anthropic API key、或希望工具自己付 API 账单的人。

## 特性一览

| 能力 | 说明 |
|---|---|
| 📚 文献检索精读 | 多源检索 + 去重 + 引用排序；下载 OA PDF；双语对照笔记自动落盘 |
| ✍️ 论文写作润色 | 中英互译润色、目标期刊风格适配、审稿意见 point-by-point 回复、长文批量改写 |
| 🔍 审稿 / 思路评估 | 创新 / 严谨 / 清晰 / 意义 四维打分 + 行级问题 + major/minor 修改清单 |
| 🧠 领域知识 | 能源/动力工程术语、期刊圈、方法论陷阱直接写进提示词 |
| 🗂️ 跨会话笔记 | workspace 里所有 markdown 按关键词检索回查 |
| 🔌 免费数据源 | OpenAlex / Crossref / Semantic Scholar / arXiv / Unpaywall，无需 key |
| 🛡️ 写入沙箱 | 写文件仅限 `workspace/` 下，不会误碰外部文件 |

---

## 安装

需要 Python 3.11+ 和一个 [Anthropic API key](https://console.anthropic.com)。

### 方式一：pipx（推荐，最干净）

```bash
pipx install git+https://github.com/1844514356zjc-dev/research-agent.git
```

装好后直接有 `research-agent` 命令。`workspace/` 会建在**你运行命令的当前目录**下。

### 方式二：pip

```bash
pip install git+https://github.com/1844514356zjc-dev/research-agent.git
```

### 方式三：从源码（适合二次开发）

```bash
git clone https://github.com/1844514356zjc-dev/research-agent.git
cd research-agent
pip install -r requirements.txt
```

### 配置 API key

在**你打算运行的目录**下建一个 `.env`（任何方式设置环境变量都行）：

```bash
cp .env.example .env   # 或自己新建
# 编辑 .env：
#   ANTHROPIC_API_KEY=sk-ant-...        （必填，https://console.anthropic.com）
#   UNPAYWALL_EMAIL=you@your-school.edu  （选填，填真实邮箱，找 OA PDF 更顺）
#   MODEL=claude-sonnet-5                （选填，覆盖默认模型）
```

> `.env` 已在 `.gitignore` 里，不会被提交。

---

## 快速开始（30 秒上手）

```bash
cd ~/my-research        # 任意你做研究的目录
research-agent literature
```

进入交互界面后直接打字提问：

```
你: 检索近 5 年 sCO2 布雷顿循环的高被引论文，精读最高引用那篇并出中文笔记
```

它会自己：多源检索 → 去重排序 → 找开放获取 PDF → 下载精读 → 生成双语笔记存到 `workspace/notes/`。全过程流式打印，你能看到它在调什么工具、读到什么。

---

## 使用手册

启动：

```bash
research-agent                       # 交互式选模式
research-agent literature            # 直入文献模式
research-agent writing --model opus  # 写作模式 + opus
research-agent review  --model opus  # 审稿推荐用 opus
```

> 从源码运行则把 `research-agent` 换成 `python main.py`。

### 模式一：文献检索与精读（`literature`）

最常用的模式。典型提问：

- `检索有机朗肯循环（ORC）工质筛选的综述，要近 5 年、高被引的`
- `这篇 DOI 10.1016/j.energy.2019.115900 主要讲了什么？给我出中文笔记`
- `之前读过哪些 R245fa 相关的？`（自动调 `search_notes` 回查本地笔记）

它会优先用 `search_papers(source="all")` 多源去重，挑高被引的精读，输出结构化双语笔记（研究问题 / 方法 / 关键参数与工况 / 主要结论 / 局限 / 对你研究的启示），并存到 `workspace/notes/`。

### 模式二：论文写作与润色（`writing`）

- 直接粘一段中文方法描述：`改写成 Applied Energy 风格的英文，保留所有数值与单位`
- 粘审稿意见：`逐条回复，point-by-point，语气专业`
- 长文批量改写（见 `/rewrite` 命令）

### 模式三：审稿 / 思路评估（`review`）

- `/pdf ~/Downloads/manuscript.pdf` 载入稿件
- `评估创新性与方法严谨性，给 major/minor 清单`
- 输出：四维打分（1–5）+ 行级问题 + 可执行修改方向 + 总体结论（接收/小修/大修/拒）

### 命令速查表

在交互界面里以 `/` 开头：

| 命令 | 作用 | 示例 |
|---|---|---|
| `/pdf <路径...>` | 预载一篇或多篇 PDF（支持通配符） | `/pdf ~/Downloads/*.pdf` |
| `/rewrite <路径> [--to en\|zh] [--style "..."]` | 批量改写 md/txt：逐节翻译/润色，存成带 `-en`/`-zh` 后缀的新文件 | `/rewrite drafts/methods.md --to en --style "Applied Energy"` |
| `/notes [关键词]` | 列出已有笔记；给关键词则跨笔记检索 | `/notes orc 工质` |
| `/mode <模式>` | 切模式（清空历史）：`literature` / `writing` / `review` | `/mode writing` |
| `/model <名>` | 切模型：`sonnet` / `opus` / `haiku` 或完整 id | `/model opus` |
| `/save <名>` | 把当前对话存到 `workspace/notes/对话记录-<名>.md` | `/save orc-survey` |
| `/clear` | 清空当前模式历史 | |
| `/help` `/quit` | 帮助 / 退出 | |

---

## 工具与数据源

Agent 在对话中会自己选择调用下列工具（你也可以在提问里点名要求）：

**检索类（全部免费、无需 key）**

| 工具 | 数据源 | 能做什么 |
|---|---|---|
| `search_papers` | OpenAlex / Crossref / Semantic Scholar / arXiv | 关键词检索；`source="all"` 多源去重合并、按引用数排序 |
| `get_citations` | Semantic Scholar | 查"谁引用了本文"或"本文的参考文献" |
| `get_open_pdf` | Unpaywall | 按 DOI 找合法开放获取 PDF 链接 |

**本地类**

| 工具 | 能做什么 |
|---|---|
| `read_pdf` | 读本地 PDF 文本，支持 `pages="1-5"` 或 `"2,4,6"` 分段 |
| `download_pdf` | 下载 URL 的 PDF 到 `workspace/papers/` |
| `read_file` / `write_file` | 读写本地文本（写入仅限 `workspace/` 沙箱） |
| `search_notes` / `list_notes` | 跨会话笔记关键词检索 / 列出全部笔记 |

---

## 配置

所有配置走环境变量（`.env` 或 shell）：

| 变量 | 必填 | 说明 |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | 你的 Claude API key |
| `MODEL` | — | 默认 `claude-sonnet-5`；审稿推荐 `claude-opus-4-8` |
| `UNPAYWALL_EMAIL` | — | 找 OA PDF 用的联系邮箱，填**真实邮箱**（`example.com` 会被拒） |

**模型建议**：日常检索/精读/写作用 `sonnet`（快、够用）；重要的审稿或深度思路评估切 `opus`（更慢更贵但更深）。

---

## 典型工作流

### ① 开题文献综述

```bash
research-agent literature
你: 搜一下"超临界 CO2 再压缩布雷顿循环 + 太阳能"近 5 年高被引论文，去重后给我前 10 篇
你: 第 1、3、7 篇各出一份中文精读笔记
你: 综合这几篇，给我一个研究空白分析
你: /save sco2-solar-survey
```

### ② 中文方法段 → Applied Energy 英文

```bash
research-agent writing
你: /rewrite drafts/methods-zh.md --to en --style "Applied Energy"
```

逐节给"原文要点 → 改写"对照，保留数据/单位/变量符号/公式编号，成品存为 `drafts/methods-zh-en.md`。

### ③ 投稿前自审

```bash
research-agent review --model opus
你: /pdf ~/Downloads/manuscript.pdf
你: 按 Energy 期刊标准评估，重点看创新性和方法严谨性，给 major/minor 清单
你: /save self-review-v1
```

---

## 示意会话（illustrative）

下面是一次文献精读交互的样子（输出为示意，非实时截图）：

```
科研 Agent · 能源/动力工程
模式: literature   模型: claude-sonnet-5   工作区: /Users/me/my-research/workspace

你: 检索 ORC 工质筛选高被引论文，精读最高引用那篇

→ 调用 1 个工具: search_papers
来源: all（多源去重合并，响应 3/4 源）| 查询: organic rankine cycle working fluid selection
去重后 5 条（按引用数排序）
1. Effect of working fluids on organic Rankine cycle for waste heat recovery (2004) [cited=761]
   DOI: 10.1016/j.energy.2004.01.004 ...
→ 调用 2 个工具: get_open_pdf, read_pdf

最高被引是 Liu & Chien (2004)，精读如下：
【研究问题】ORC 用于低温余热回收时，工质如何影响性能 ……
【方法】对 11 种工质在相同工况下做热力对比 ……
【关键结论】R245fa 在 120°C 热源下热效率最高（8.5%）……
【局限】未考虑工质热稳定性上限 ……
【对本研究的启示】……

→ 已写入: workspace/notes/liu-2004-orc-working-fluids.md  (1.8KB)
```

---

## 项目结构

```
research-agent/
├── main.py            # CLI 入口 + REPL + 斜杠命令
├── agent.py           # 流式 tool-calling 循环
├── tools.py           # 9 个工具实现 + JSON schema（检索/本地/笔记）
├── prompts.py         # 三模式系统提示词 + 能源/动力工程领域知识
├── test_offline.py    # 离线确定性测试（CI 跑）
├── pyproject.toml     # 打包配置 + research-agent 命令入口
├── requirements.txt
└── workspace/         # 运行时输出（gitignore），在调用目录下自动建
    ├── notes/         # 文献精读笔记、对话存档
    ├── drafts/        # 写作/润色成品
    ├── reviews/       # 审稿记录
    └── papers/        # 下载的 PDF
```

---

## 常见问题

**需要联网吗？**　需要。检索走学术 API、改写走 Claude API，都要联网。读本地 PDF 不需要。

**API 大概多少钱？**　主要成本在 Claude 调用。Sonnet 做一次文献精读（含几次工具调用）通常几百到两三千 token，几分钱量级。Opus 贵约 5–15 倍，建议只在深度审稿时用。

**检索被限流（429）怎么办？**　Semantic Scholar 与 OpenAlex 对无 key 请求有额度限制，偶发 429。`source="all"` 会自动跳过失败源、用其余源补上；过一会儿再试即可。`UNPAYWALL_EMAIL` 填真实邮箱可进 polite pool，限额更高。

**能读收费论文吗？**　只能读开放获取（OA）的全文。非 OA 的论文仍可检索到元数据（标题/作者/年/DOI/引用数/摘要），但下载不到 PDF——这是版权所限。

**笔记/草稿存在哪？**　在**你运行命令的当前目录**下的 `workspace/` 里，纯 markdown，随时可看可改可备份。换目录运行就换一份 workspace。

**支持其他学科吗？**　领域知识写在 `prompts.py` 的 `DOMAIN_KNOWLEDGE` 里，改那段就能迁到别的学科（化学、材料、机械……）。检索/写作工具本身学科无关。

**会话历史会留多久？**　历史只在当前会话内存里。`/save` 可存档；下次启动是新会话——但 `workspace/` 里的笔记是持久积累的。

---

## 已知局限

- 需要 Anthropic API key，调用按量计费（用户自理）
- 笔记检索是关键词匹配，没有向量语义检索
- 只能获取开放获取的全文 PDF，非 OA 论文只能拿到元数据
- arXiv / Semantic Scholar 偶有波动或限流，代码侧已优雅降级

---

## 贡献

欢迎提 issue 或 PR。小的改动直接提；大的改动请先开 issue 讨论方向。

跑测试：

```bash
python test_offline.py            # 离线确定性测试，无需网络/key
python -m py_compile *.py         # 语法检查
```

CI（GitHub Actions）会在每次推送时跑 Python 3.11–3.14 矩阵。

---

## 许可证

[MIT](LICENSE)
