import asyncio
import json
import os
from contextlib import AsyncExitStack

from dotenv import load_dotenv
from guardrails import Guard
from guardrails.hub import DetectJailbreak, RestrictToTopic
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from openai import OpenAI


class MCPManager:
    def __init__(self, servers: dict[str, str]):
        self.servers = servers
        self.clients = {}
        self.tools = []
        self._stack = AsyncExitStack()

    async def __aenter__(self):
        for url in self.servers.values():
            read, write, _ = await self._stack.enter_async_context(
                streamable_http_client(url)
            )
            session = await self._stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            tools_resp = await session.list_tools()
            for t in tools_resp.tools:
                self.clients[t.name] = session
                self.tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": t.name,
                            "description": t.description,
                            "parameters": t.inputSchema,
                        },
                    }
                )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._stack.aclose()

    async def call_tool(self, name: str, args: dict) -> str:
        result = await self.clients[name].call_tool(name, arguments=args)
        return result.content[0].text


async def handle_turn(
    client: OpenAI, messages: list, mcp: MCPManager, guard_topic: Guard
) -> str:
    for _ in range(12):
        response = client.chat.completions.create(
            model="",
            messages=messages,
            tools=mcp.tools,
            tool_choice="auto",
            max_completion_tokens=1000,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
        msg = response.choices[0].message
        if msg.tool_calls:
            messages.append(msg.model_dump())
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                result = await mcp.call_tool(func_name, func_args)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": str(result),
                    }
                )
        else:
            content = (msg.content or "").strip()
            try:
                guard_topic.validate(content)
            except Exception as e:
                content = f"[OFF_TOPIC] {e}"
            messages.append({"role": "assistant", "content": content})
            return content
    return "I could not complete given request."


async def chat():
    load_dotenv()
    servers = {
        "weather": "http://127.0.0.1:8002/mcp",
        "tavily": "https://mcp.tavily.com/mcp"
        + "?tavilyApiKey="
        + os.getenv("TAVILY_API_KEY", ""),
    }
    client = OpenAI(
        api_key=os.getenv("VLLM_API_KEY", "EMPTY"),
        base_url="http://127.0.0.1:8000/v1",
    )

    system = (
        "You are a travel planning assistant. Respond only to trip-planning related requests."
        "Call tools when appropriate. If the request is unrelated, decline."
    )

    guard_jailbreak = Guard().use(DetectJailbreak, on_fail="exception")
    guard_topic = Guard().use(
        RestrictToTopic,
        valid_topics=["travel", "trip planning", "vacation", "tourism"],
        disable_llm=True,
        on_fail="exception",
    )

    messages = [{"role": "system", "content": system}]

    async with MCPManager(servers) as mcp:
        while True:
            user_input = input("> ").strip()
            if user_input.lower() in {"exit", "quit"}:
                break
            if not user_input:
                continue
            try:
                guard_jailbreak.validate(user_input)
            except Exception as e:
                print(f"[BLOCKED] {e}")
                continue
            messages.append({"role": "user", "content": user_input})
            reply = await handle_turn(client, messages, mcp, guard_topic)
            print(reply)


if __name__ == "__main__":
    asyncio.run(chat())
