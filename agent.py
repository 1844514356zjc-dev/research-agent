"""流式 tool-calling 循环。

用法:
    from agent import ResearchAgent
    ag = ResearchAgent(mode="literature", model="claude-sonnet-5")
    ag.add_user("检索近 5 年 sCO2 布雷顿循环高被引论文")
    ag.run_turn()  # 流式打印，自动执行工具，直到模型结束本轮
"""

from __future__ import annotations
import os

import anthropic
from rich.console import Console

from prompts import SYSTEM_FOR
from tools import TOOLS, dispatch

console = Console()

MAX_TOOL_ITER = 8  # 单轮最多工具调用轮次，防死循环


class ResearchAgent:
    def __init__(self, mode: str = "literature", model: str | None = None):
        if mode not in SYSTEM_FOR:
            raise ValueError(f"未知模式: {mode}（可选: {list(SYSTEM_FOR)}）")
        self.mode = mode
        self.model = model or os.getenv("MODEL") or "claude-sonnet-5"
        self.system = SYSTEM_FOR[mode]
        self.messages: list[dict] = []
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError(
                "未设置 ANTHROPIC_API_KEY。请在 .env 或环境变量中配置。"
            )
        self.client = anthropic.Anthropic(api_key=key)

    def reset(self, mode: str | None = None) -> None:
        if mode:
            if mode not in SYSTEM_FOR:
                raise ValueError(f"未知模式: {mode}")
            self.mode = mode
            self.system = SYSTEM_FOR[mode]
        self.messages = []

    def add_user(self, text: str) -> None:
        self.messages.append({"role": "user", "content": text})

    def run_turn(self) -> str:
        """执行一轮：流式打印文本，遇到 tool_use 自动执行并续跑。返回最终文本。"""
        final_text = ""
        for _ in range(MAX_TOOL_ITER):
            with self.client.messages.stream(
                model=self.model,
                max_tokens=8192,
                system=self.system,
                tools=TOOLS,
                messages=self.messages,
            ) as stream:
                console.print()  # 留白
                for text in stream.text_stream:
                    console.print(text, end="")
                    final_text += text
                final = stream.get_final_message()

            if final.stop_reason == "tool_use":
                self.messages.append({"role": "assistant", "content": final.content})
                tool_calls = [b for b in final.content if getattr(b, "type", None) == "tool_use"]
                console.print(
                    f"\n[dim]→ 调用 {len(tool_calls)} 个工具: "
                    f"{', '.join(b.name for b in tool_calls)}[/]"
                )
                for b in tool_calls:
                    result = dispatch(b.name, dict(b.input))
                    self.messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": b.id,
                            "content": result,
                        }],
                    })
                continue  # 把工具结果喂回去，继续生成
            break  # end_turn / 其他停止原因

        else:
            console.print("\n[yellow]⚠ 达到单轮工具调用上限，已停止。[/]")

        return final_text
