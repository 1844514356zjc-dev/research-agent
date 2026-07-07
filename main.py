#!/usr/bin/env python3
"""科研实用 Agent — CLI 入口 + REPL。

用法:
    research-agent                       # 交互式选模式（首次自动跑配置向导）
    research-agent literature            # 直入文献模式
    research-agent writing --model opus  # 写作模式 + opus（审稿推荐）
"""

from __future__ import annotations
import argparse
import glob
import os
import shlex
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from prompts import (MODELS, MODES, OUTPUT_LANG, LANG_LABELS,
                     SUPPORTED_LANGS, examples_for)
from tools import read_pdf, WORKSPACE

load_dotenv()  # 读 .env 里的 ANTHROPIC_API_KEY / MODEL / OUTPUT_LANG

console = Console()

HELP = """\
[命令]（在对话中输入，以 / 开头）
  /examples            显示当前模式的示例提问
  /pdf <路径...>       预载一篇或多篇 PDF（支持通配符），如 /pdf ~/Downloads/*.pdf
  /rewrite <路径>      批量改写一个 md/txt 文件：逐节翻译/润色并存新文件
                       可选 --to en|zh（默认 en）、--style "期刊或风格名"
  /notes [关键词]      列出已有笔记；给关键词则跨笔记检索
  /mode <模式>         切换模式：literature / writing / review（清空历史）
  /model <名>          切换模型：sonnet / opus / haiku 或完整模型 id
  /lang <zh|en|ja|es|de>  实时切换输出语言
  /usage               查看本会话 token 用量
  /status              查看当前状态（模式/语言/模型/工作区/消息数/用量）
  /save <名>           把当前对话保存到 workspace/notes/对话记录-<名>.md
  /clear               清空当前模式的历史
  /help, /?            显示本帮助
  /quit, /exit         退出
"""


def resolve_model(name: str) -> str:
    key = name.lower()
    if key in MODELS:
        return MODELS[key]
    return name  # 当作完整 model id


def banner(agent) -> None:
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="cyan", no_wrap=True)
    table.add_column()
    table.add_row("模式", agent.mode)
    table.add_row("输出语言", f"{agent.lang}（{LANG_LABELS.get(agent.lang, '?')}）")
    table.add_row("模型", agent.model)
    table.add_row("工作区", str(WORKSPACE))
    console.print(Panel(table, title="[bold]科研 Agent[/]  ·  能源/动力工程",
                        border_style="cyan", expand=False))
    ex = examples_for(agent.mode, agent.lang)
    if ex:
        console.print("[dim]试试这些（直接输入即可）：[/]")
        for e in ex:
            console.print(f"  [cyan]•[/] {e}")
    console.print(f"\n[dim]输入 /help 看全部命令；/examples 看更多示例。[/]")


def choose_mode() -> str:
    console.print(Panel(
        "\n[1] 文献检索与精读  literature\n"
        "[2] 论文写作与润色  writing\n"
        "[3] 审稿 / 思路评估  review\n",
        title="选择模式", border_style="cyan"))
    while True:
        c = Prompt.ask("模式 [1/2/3]", default="1")
        m = {"1": "literature", "2": "writing", "3": "review"}.get(c.strip())
        if m:
            return m
        console.print("[red]无效选择[/]")


# ---------------------------------------------------------------------------
# 首次运行向导：检测不到 API key 时引导配置 .env
# ---------------------------------------------------------------------------

def _write_env(values: dict[str, str]) -> None:
    """把 values 写入 cwd 的 .env，保留不在 values 里的既有行。"""
    path = Path(".env")
    keep: list[str] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            k = line.split("=", 1)[0].strip()
            if k and k not in values:
                keep.append(line)
    out = keep + [f"{k}={v}" for k, v in values.items()]
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def run_setup_wizard() -> bool:
    """交互式配置 .env。返回 True 表示已写入 key。"""
    console.print(Panel(
        "首次使用？我来帮你配置（30 秒）。\n"
        "需要：Anthropic API key —— 在 https://console.anthropic.com → API Keys 获取。",
        title="[bold]首次运行向导[/]", border_style="cyan"))

    try:
        key = Prompt.ask("1) Anthropic API key（输入时不显示）", password=True).strip()
        if not key:
            console.print("[yellow]未提供 key，向导中止。配置好后重试。[/]")
            return False

        detected = OUTPUT_LANG
        console.print(f"2) 输出语言（检测到系统语言：[cyan]{detected}[/]，"
                      f"可选 {'/'.join(SUPPORTED_LANGS)}）")
        lang = Prompt.ask("   输出语言", default=detected).strip().lower()[:2]
        if lang not in LANG_LABELS:
            lang = detected

        console.print("3) 默认模型：sonnet（推荐，日常够用）/ opus（深度审稿）/ haiku（最快最省）")
        model_in = Prompt.ask("   默认模型", default="sonnet").strip().lower()
        model_id = resolve_model(model_in) if model_in else "claude-sonnet-5"
    except (EOFError, KeyboardInterrupt):
        console.print("\n[yellow]向导已取消。[/]")
        return False

    _write_env({
        "ANTHROPIC_API_KEY": key,
        "OUTPUT_LANG": lang,
        "MODEL": model_id,
    })
    console.print(f"[green]✓ 已写入 .env（输出语言: {LANG_LABELS[lang]}，模型: {model_id}）[/]")
    load_dotenv(override=True)
    return True


# ---------------------------------------------------------------------------
# 斜杠命令实现
# ---------------------------------------------------------------------------

def load_pdfs_into(agent, paths: list[str]) -> None:
    if not paths:
        console.print("[red]用法: /pdf <一个或多个路径，支持通配符>[/]")
        return
    total = 0
    for path in paths:
        text = read_pdf(path)
        total += len(text)
        agent.add_user(
            f"（系统已预载 PDF：{path}\n以下是全文（或部分页），后续问题请基于此回答。）\n\n{text}"
        )
        console.print(f"[green]✓ 已预载：{path}[/]")
    console.print(f"[dim]共载入 {len(paths)} 篇，约 {total} 字符。直接提问即可。[/]")


def do_rewrite(agent, arg: str) -> None:
    """批量改写：读文件 → 逐节翻译/润色 → 用 write_file 存新文件。"""
    try:
        toks = shlex.split(arg)
    except ValueError:
        toks = arg.split()
    if not toks:
        console.print('[red]用法: /rewrite <文件路径> [--to en|zh] [--style "期刊或风格"][/]')
        return
    path = toks[0]
    to, style = "en", ""
    i = 1
    while i < len(toks):
        if toks[i] == "--to" and i + 1 < len(toks):
            to = toks[i + 1]; i += 2
        elif toks[i] == "--style" and i + 1 < len(toks):
            style = toks[i + 1]; i += 2
        else:
            i += 1
    from tools import read_file
    text = read_file(path)
    if text.startswith("[") and ("不存在" in text or "失败" in text):
        console.print(f"[red]{text}[/]")
        return
    target = "英文（学术语域）" if to.lower().startswith("en") else "中文"
    style_hint = f"，风格参考《{style}》" if style else ""
    prompt = (
        f"请把下面这份文档逐节改写为{target}{style_hint}。要求：\n"
        f"1) 保留所有原始数据、单位、变量符号、图表与公式编号；\n"
        f"2) 按 ## 标题逐节处理，每节先给「原文要点 → 改写」对照；\n"
        f"3) 专业术语保留英文（如 Rankine cycle、exergy），中→英时用学术语域、避免口语；\n"
        f"4) 改写完成后，用 write_file 把完整成品存到同一目录的新文件，"
        f"文件名在原基础上加后缀 -{to}（如 methods.md → methods-{to}.md）。\n\n"
        f"--- 原文（{path}）---\n{text}"
    )
    agent.add_user(prompt)
    console.print(f"[green]✓ 开始批量改写 {path}（{len(text)} 字符）→ {target}{style_hint}[/]")
    try:
        agent.run_turn()
    except Exception as e:
        console.print(f"\n[red]✗ 改写出错: {e}[/]")


def do_notes(arg: str) -> None:
    from tools import list_notes, search_notes
    arg = arg.strip()
    console.print(search_notes(arg) if arg else list_notes())


def do_status(agent) -> None:
    t = Table(show_header=False, box=None, padding=(0, 2))
    t.add_column(style="cyan", no_wrap=True)
    t.add_column()
    t.add_row("模式", agent.mode)
    t.add_row("输出语言", f"{agent.lang}（{LANG_LABELS.get(agent.lang, '?')}）")
    t.add_row("模型", agent.model)
    t.add_row("工作区", str(WORKSPACE))
    t.add_row("消息数", str(len(agent.messages)))
    t.add_row("用量", agent.usage_summary())
    console.print(t)


def save_transcript(agent, name: str) -> None:
    from tools import write_file
    parts = [f"# 对话记录 · {agent.mode} · {agent.model}\n"]
    for m in agent.messages:
        role = m["role"]
        c = m["content"]
        if isinstance(c, str):
            parts.append(f"\n## {role}\n\n{c}\n")
        elif isinstance(c, list):
            for b in c:
                t = getattr(b, "type", None)
                if t == "text":
                    parts.append(f"\n## {role}\n\n{b.text}\n")
                elif t == "tool_use":
                    parts.append(f"\n## {role} (tool: {b.name})\n\n```{b.input}```\n")
                elif t == "tool_result":
                    pass  # 工具结果体量大，存盘时跳过
    content = "\n".join(parts)
    out = write_file(f"notes/对话记录-{name}.md", content)
    console.print(f"[green]✓ {out}[/]")


def repl(agent) -> None:
    banner(agent)
    while True:
        try:
            user = Prompt.ask("[bold cyan]你[/]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]再见[/]")
            return
        if not user.strip():
            continue

        if user.startswith("/"):
            cmd, *rest = user[1:].split(None, 1)
            arg = rest[0].strip() if rest else ""
            if cmd in ("quit", "exit"):
                console.print("[dim]再见[/]")
                return
            if cmd in ("help", "?"):
                console.print(HELP)
                continue
            if cmd == "examples":
                ex = examples_for(agent.mode, agent.lang)
                if ex:
                    for e in ex:
                        console.print(f"  [cyan]•[/] {e}")
                else:
                    console.print("[dim]（暂无示例）[/]")
                continue
            if cmd == "mode" and arg in MODES:
                agent.reset(arg)
                console.print(f"[green]✓ 已切换到 {arg} 模式（历史已清空）[/]")
                continue
            if cmd == "model" and arg:
                agent.model = resolve_model(arg)
                console.print(f"[green]✓ 模型: {agent.model}[/]")
                continue
            if cmd == "lang" and arg:
                code = arg.strip().lower()[:2]
                if code in LANG_LABELS:
                    agent.set_lang(code)
                    console.print(f"[green]✓ 输出语言: {LANG_LABELS[code]}（{code}）"
                                  f"——下次回复起生效。[/]")
                else:
                    console.print(f"[red]不支持。可选: {'/'.join(SUPPORTED_LANGS)}[/]")
                continue
            if cmd == "usage":
                console.print(agent.usage_summary())
                continue
            if cmd == "status":
                do_status(agent)
                continue
            if cmd == "pdf":
                if not arg:
                    console.print("[red]用法: /pdf <一个或多个路径，支持通配符>[/]")
                    continue
                paths = []
                for tok in arg.split():
                    tok = os.path.expanduser(tok)
                    matches = sorted(glob.glob(tok))
                    paths.extend(matches if matches else [tok])
                load_pdfs_into(agent, paths)
                continue
            if cmd == "rewrite" and arg:
                do_rewrite(agent, arg)
                continue
            if cmd == "notes":
                do_notes(arg)
                continue
            if cmd == "save" and arg:
                save_transcript(agent, arg)
                continue
            if cmd == "clear":
                agent.reset()
                console.print("[green]✓ 历史已清空[/]")
                continue
            console.print("[red]命令无效或参数缺失。/help 查看用法。[/]")
            continue

        agent.add_user(user)
        try:
            agent.run_turn()
        except Exception as e:
            console.print(f"\n[red]✗ 出错: {e}[/]")
            console.print("[dim]可继续输入；若反复出错用 /clear 清空历史。[/]")


def main() -> int:
    ap = argparse.ArgumentParser(description="科研实用 Agent — 能源/动力工程")
    ap.add_argument("mode", nargs="?", choices=list(MODES),
                    help="直接进入的模式：literature / writing / review")
    ap.add_argument("--model", default=None,
                    help="模型：sonnet / opus / haiku 或完整 id；默认 sonnet")
    args = ap.parse_args()

    # 没配置 API key → 跑首次运行向导
    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print("[yellow]✗ 未检测到 ANTHROPIC_API_KEY[/]")
        if not run_setup_wizard():
            return 1

    try:
        from agent import ResearchAgent
        agent = ResearchAgent(
            mode=args.mode or choose_mode(),
            model=resolve_model(args.model) if args.model else None,
        )
    except RuntimeError as e:
        console.print(f"[red]✗ {e}[/]")
        console.print("[dim]配置好 .env（ANTHROPIC_API_KEY）后重试。[/]")
        return 1
    except ValueError as e:
        console.print(f"[red]✗ {e}[/]")
        return 1

    try:
        repl(agent)
    except KeyboardInterrupt:
        console.print("\n[dim]再见[/]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
