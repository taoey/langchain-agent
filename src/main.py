import streamlit as st
import os
import requests
# from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama
# 加载环境变量（存放OpenAI API Key）
# load_dotenv()
# 页面配置
st.set_page_config(page_title="LangChain Agent 聊天界面", page_icon="🤖", layout="wide")
st.title("🤖 LangChain Agent 聊天助手")

# ---------------------- 获取可用模型列表 ----------------------
def get_available_models(base_url: str) -> list:
    """从 ollama 服务器获取可用的模型列表"""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            return [model['name'] for model in models_data.get('models', [])]
        else:
            return []
    except Exception as e:
        st.error(f"获取模型列表失败: {str(e)}")
        return []

# ---------------------- 1. 初始化会话状态 ----------------------
# 会话状态（session_state）：保存页面刷新不丢失的数据
if "messages" not in st.session_state:
    # 初始化对话历史
    st.session_state.messages = [AIMessage(content="你好！我是你的AI助手，有什么可以帮助你的？")]

if "base_url" not in st.session_state:
    # 默认 ollama 服务器地址
    st.session_state.base_url = "http://192.168.3.25:11434"

if "selected_model" not in st.session_state:
    # 默认模型名称
    st.session_state.selected_model = "qwen3.5:4b"

# 初始化 LLM
if "llm" not in st.session_state:
    st.session_state.llm = ChatOllama(
        model=st.session_state.selected_model,
        base_url=st.session_state.base_url
    )

# ---------------------- 2. 侧边栏配置 ----------------------
with st.sidebar:
    st.header("⚙️ 配置项")
    
    # Ollama 服务器配置
    st.subheader("🌐 Ollama 服务器")
    base_url = st.text_input(
        "服务器地址",
        value=st.session_state.base_url,
        help="Ollama 服务器地址，例如: http://192.168.3.25:11434"
    )
    
    # 更新服务器地址
    if base_url != st.session_state.base_url:
        st.session_state.base_url = base_url
    
    # 获取并选择模型
    st.subheader("🤖 模型选择")
    
    # 刷新模型列表按钮
    if st.button("🔄 刷新模型列表"):
        with st.spinner("正在获取模型列表..."):
            available_models = get_available_models(st.session_state.base_url)
            st.session_state.available_models = available_models
    
    # 如果还没有获取模型列表，先获取一次
    if "available_models" not in st.session_state:
        with st.spinner("正在获取模型列表..."):
            st.session_state.available_models = get_available_models(st.session_state.base_url)
    
    # 显示可用模型
    if st.session_state.available_models:
        selected_model = st.selectbox(
            "选择模型",
            options=st.session_state.available_models,
            index=st.session_state.available_models.index(st.session_state.selected_model) 
                  if st.session_state.selected_model in st.session_state.available_models 
                  else 0,
            help="从下拉列表中选择要使用的模型"
        )
        
        # 如果选择了不同的模型，重新初始化 LLM
        if selected_model != st.session_state.selected_model:
            st.session_state.selected_model = selected_model
            st.session_state.llm = ChatOllama(
                model=st.session_state.selected_model,
                base_url=st.session_state.base_url
            )
            st.success(f"已切换到模型: {selected_model}")
    else:
        st.warning("未找到可用模型，请检查服务器地址")
        selected_model = st.text_input(
            "手动输入模型名称",
            value=st.session_state.selected_model,
            help="如果自动获取失败，可以手动输入模型名称"
        )
        if selected_model != st.session_state.selected_model:
            st.session_state.selected_model = selected_model
            st.session_state.llm = ChatOllama(
                model=st.session_state.selected_model,
                base_url=st.session_state.base_url
            )
    
    # 调整模型温度（0=严谨，1=创意）
    st.subheader("🎛️ 参数设置")
    temperature = st.slider("模型温度", 0.0, 1.0, 0.7, step=0.1)
    st.session_state.llm.temperature = temperature
    
    # 显示当前配置
    st.info(f"📍 当前使用: {st.session_state.selected_model}\n🌐 服务器: {st.session_state.base_url}")
    
    # 清空对话按钮
    if st.button("🗑️ 清空对话历史"):
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

        with st.status("正在思考...", expanded=True) as status:
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