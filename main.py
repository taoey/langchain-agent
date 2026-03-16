import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama
# 加载环境变量（存放OpenAI API Key）
load_dotenv()
# 页面配置
st.set_page_config(page_title="LangChain Agent 聊天界面", page_icon="🤖", layout="wide")
st.title("🤖 LangChain Agent 聊天助手")

# ---------------------- 1. 初始化会话状态 ----------------------
# 会话状态（session_state）：保存页面刷新不丢失的数据
if "messages" not in st.session_state:
    # 初始化对话历史
    st.session_state.messages = [AIMessage(content="你好！我是你的AI助手，有什么可以帮助你的？")]
if "llm" not in st.session_state:
    # 初始化LLM（替换为你的LangChain Agent）
    st.session_state.llm =ChatOllama(
    model="qwen3.5:4b",
    # model="deepseek-r1:7b",
    # model="deepseek-r1:7b",
    base_url="http://192.168.3.25:11434"
)

# ---------------------- 2. 侧边栏配置 ----------------------
with st.sidebar:
    st.header("⚙️ 配置项")
    # 调整模型温度（0=严谨，1=创意）
    temperature = st.slider("模型温度", 0.0, 1.0, 0.7, step=0.1)
    st.session_state.llm.temperature = temperature
    # 清空对话按钮
    if st.button("清空对话历史"):
        st.session_state.messages = [AIMessage(content="你好！我是你的AI助手，有什么可以帮助你的？")]

# ---------------------- 3. 展示对话历史 ----------------------
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        # 用户消息
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage):
        # AI消息
        st.chat_message("assistant").write(msg.content)

# ---------------------- 4. 处理用户输入 ----------------------
# 聊天输入框（页面底部）
if user_input := st.chat_input("请输入你的问题..."):
    # 1. 添加用户消息到历史
    st.session_state.messages.append(HumanMessage(content=user_input))
    st.chat_message("user").write(user_input)

    # 2. 调用LLM生成回复（流式输出）
    with st.chat_message("assistant"):
        # 占位符：实时更新回复内容
        msg_placeholder = st.empty()
        # full_response = "你好呀：" + user_input
        full_response = ""
        
        # 流式调用LLM
        for chunk in st.session_state.llm.stream([HumanMessage(content=user_input)]):
            full_response += chunk.content
            # 实时更新（加光标动画）
            msg_placeholder.markdown(full_response + "▌")
        
        # 移除光标，显示最终回复
        msg_placeholder.markdown(full_response)
        
        # 3. 添加AI回复到历史
        st.session_state.messages.append(AIMessage(content=full_response))