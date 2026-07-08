"""流式 tool-calling 循环。

用法:
    from agent import ResearchAgent
    ag = ResearchAgent(mode="literature")             # 语言自动检测 / 读 OUTPUT_LANG
    ag.add_user("检索近 5 年 sCO2 布雷顿循环高被引论文")
    ag.run_turn()  # 流式打印，自动执行工具，直到模型结束本轮
    ag.set_lang("en")                                  # 实时切输出语言
"""

from __future__ import annotations
import os

import anthropic
from rich.console import Console

from prompts import system_for, MODELS, OUTPUT_LANG
from tools import TOOLS, dispatch

console = Console()

MAX_TOOL_ITER = 8  # 单轮最多工具调用轮次，防死循环


class ResearchAgent:
    def __init__(self, mode: str = "literature", model: str | None = None,
                 lang: str | None = None):
        self.mode = mode
        self.lang = lang or OUTPUT_LANG
        self.model = model or os.getenv("MODEL") or "claude-sonnet-5"
        self.system = system_for(mode, self.lang)
        self.messages: list[dict] = []
        # token 用量（累计）
        self.total_input = 0
        self.total_output = 0
        self.turns = 0
        # 认证：优先 ANTHROPIC_AUTH_TOKEN（Bearer，智谱等代理常用），
        # 其次 ANTHROPIC_API_KEY（x-api-key，Anthropic 官方）。
        auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if auth_token:
            client_kwargs = {"auth_token": auth_token}
        elif api_key:
            client_kwargs = {"api_key": api_key}
        else:
            raise RuntimeError(
                "未设置 ANTHROPIC_API_KEY 或 ANTHROPIC_AUTH_TOKEN。请在 .env 或环境变量中配置。"
            )
        # 走代理（LiteLLM / 兼容服务）：设 ANTHROPIC_BASE_URL 指向代理的根地址，
        # SDK 会请求 {base_url}/v1/messages，由代理翻译成 DeepSeek/Qwen/OpenAI 等后端。
        self.base_url = os.getenv("ANTHROPIC_BASE_URL") or ""
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        self.client = anthropic.Anthropic(**client_kwargs)

    def reset(self, mode: str | None = None) -> None:
        if mode:
            self.mode = mode
            self.system = system_for(mode, self.lang)
        self.messages = []

    def set_lang(self, lang: str) -> None:
        self.lang = lang
        self.system = system_for(self.mode, lang)

    def add_user(self, text: str) -> None:
        self.messages.append({"role": "user", "content": text})

    def usage_summary(self) -> str:
        return (f"本会话累计：输入 {self.total_input:,} / 输出 {self.total_output:,} "
                f"tokens（共 {self.turns} 轮）")

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

            # 累计 token 用量（每次 stream 都会产生一次 input 计费）
            usage = getattr(final, "usage", None)
            if usage is not None:
                self.total_input += getattr(usage, "input_tokens", 0) or 0
                self.total_output += getattr(usage, "output_tokens", 0) or 0

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

        self.turns += 1
        if usage is not None:
            console.print(f"\n[dim]本轮: 输入 {getattr(usage,'input_tokens',0):,} / "
                          f"输出 {getattr(usage,'output_tokens',0):,} tokens | "
                          f"{self.usage_summary()}[/]")
        return final_text
