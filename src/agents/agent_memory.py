#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time           : 2026-03-19 20:48
@Author         : tao
@Python Version : 3.13.3
@Desc           : None
"""


# agent_with_memory.py - 有记忆的 Agent
from langchain_ollama import ChatOllama
from langchain.agents import create_agent, AgentState
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
import uuid

# 1. 定义工具
@tool
def get_weather(location: str) -> str:
    """获取某地天气"""
    return f"{location} 的天气：晴天，25°C"

@tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    return f"{expression} = {eval(expression)}"

# 2. 创建 Agent（带记忆）
llm = ChatOllama(model="qwen3.5:4b",base_url="http://192.168.3.25:11434")
tools = [get_weather, calculate]

agent = create_agent(
    model=llm,
    tools=tools,
    checkpointer=MemorySaver(),  # ✅ 关键：保存对话历史
    system_prompt="你是一个有帮助的助手，记住用户之前说过的话。"
)

# 3. 交互（同一 thread_id 保持记忆）
def chat_with_memory():
    thread_id = str(uuid.uuid4())  # 唯一对话 ID
    
    print("🤖 Agent 启动（具有记忆功能）\n")
    
    while True:
        user_input = input("你: ")
        if user_input.lower() in ['quit', 'exit']:
            break
        
        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config={"configurable": {"thread_id": thread_id}}  # ✅ 传入 thread_id
        )
        
        # 打印最后一条 AI 消息
        print(f"\n🤖 Agent: {result['messages'][-1].content}\n")

if __name__ == "__main__":
    chat_with_memory()