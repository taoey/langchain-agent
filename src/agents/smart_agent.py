import asyncio
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from src.tools.web_content import get_url_web_content
from src.tools.tool_time import get_current_time


llm = ChatOllama(
    model="qwen3:1.7b",
    base_url="http://192.168.3.25:11434",
    streaming=True,  # Enable token streaming (default True)
)

agent = create_agent(
    model=llm,
    tools=[],
)

def create_my_agent(base_url, model):
    llm = ChatOllama(
        model=model,
        base_url=base_url,
        streaming=True,  # Enable token streaming (default True)
    )
    return create_agent(
        model=llm,
        tools=[get_url_web_content, get_current_time],
    )

# Streaming version
# async def stream_agent():
#     async for chunk in agent.astream(
#         {
#             "messages": [
#                 {"role": "user", "content": "帮我写一个python 归并排序"},
#             ]
#         },
#         stream_mode="values",  # Streams full state snapshots per node
#     ):
#         msg = chunk["messages"][-1]
#         if msg.content:
#             print(msg.content, end="", flush=True)  # Streams tokens
#         elif hasattr(msg, 'tool_calls') and msg.tool_calls:
#             print(f"\n🛠️ Tool: {msg.tool_calls[0]['name']}", flush=True)

# # Run
# asyncio.run(stream_agent())