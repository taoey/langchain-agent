# 注意：该版本未调试，但是有些代码可借鉴，后期复杂场景可以借鉴这部分
# langchain_rag_ollama_demo.py
"""
完整 RAG Demo - 本地 Ollama 环境
要求：
1. 已安装 Ollama：https://ollama.ai
2. 已拉取模型：ollama pull llama2 (或 qwen2.5, mistral 等)
3. Ollama 服务运行在 http://localhost:11434

安装依赖：
pip install langchain langchain-community langchain-ollama faiss-cpu unstructured[pdf] pypdf
"""

import logging


from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os


# logging.basicConfig(level=logging.DEBUG)

# ============================================
# 配置
# ============================================
OLLAMA_BASE_URL = "http://192.168.3.25:11434"
EMBEDDING_MODEL = "qwen3-embedding:4b"  # 轻量级嵌入模型
LLM_MODEL = "qwen3.5:4b"  # 或 "llama2"、"mistral"
INDEX_PATH = "./faiss_index"  # 索引保存路径

# ============================================
# 步骤 1: 加载文档
# ============================================
def load_documents():
    """加载文档"""
    print("📥 加载文档...")
    
    docs = []
    
    # 方式1：从网页加载
    try:
        print("  - 从网页加载...")
        loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
        web_docs = loader.load()
        docs.extend(web_docs)
        print(f"    ✅ 加载了 {len(web_docs)} 个网页文档")
    except Exception as e:
        print(f"    ⚠️ 网页加载失败: {e}")
    
    # 方式2：从本地 PDF 加载（如果存在）
    if os.path.exists("document.pdf"):
        print("  - 从 PDF 加载...")
        loader = PyPDFLoader("document.pdf")
        pdf_docs = loader.load()
        docs.extend(pdf_docs)
        print(f"    ✅ 加载了 {len(pdf_docs)} 个 PDF 页面")
    
    # 方式3：从本地文本文件加载
    if os.path.exists("content.txt"):
        print("  - 从文本文件加载...")
        with open("content.txt", "r", encoding="utf-8") as f:
            content = f.read()
            from langchain_core.documents import Document
            docs.append(Document(page_content=content, metadata={"source": "content.txt"}))
        print(f"    ✅ 加载了本地文本文件")
    
    if not docs:
        # 如果没有文档，使用示例内容
        print("  - 使用示例内容...")
        from langchain_core.documents import Document
        example_text = """
        Agent 是由 LLM 驱动的自主系统。它能够：
        1. 理解用户问题
        2. 规划执行步骤
        3. 调用工具完成任务
        4. 根据结果迭代改进
        
        RAG（检索增强生成）是一种融合检索和生成的技术：
        1. 从知识库检索相关文档
        2. 将文档作为上下文
        3. 用 LLM 生成答案
        
        LangChain 是构建 LLM 应用的框架：
        - 提供各种工具集成
        - 支持链式调用
        - 内置记忆和持久化
        """
        docs.append(Document(page_content=example_text, metadata={"source": "example"}))
        print(f"    ✅ 使用了示例内容")
    
    print(f"📄 总共加载 {len(docs)} 个文档\n")
    return docs

# ============================================
# 步骤 2: 分割文档（分词）
# ============================================
def split_documents(docs):
    """分割文档成可检索的块"""
    print("✂️  分割文档...")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,      # 每个块的大小
        chunk_overlap=100,   # 块之间的重叠
        separators=["\n\n", "\n", "。", "！", "？", ",", "，", " ", ""]
    )
    
    chunks = splitter.split_documents(docs)
    print(f"📦 分割后得到 {len(chunks)} 个块\n")
    
    return chunks

# ============================================
# 步骤 3: 嵌入和建立向量索引
# ============================================
def create_vectorstore(chunks, use_saved_index=False):
    """创建向量存储"""
    print("🔢 创建向量索引...\n")
    
    # 初始化嵌入模型（使用本地 Ollama）
    print(f"  📌 嵌入模型: {EMBEDDING_MODEL}")
    print(f"  🌐 Ollama 地址: {OLLAMA_BASE_URL}")
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL
    )
    
    # 检查是否使用已保存的索引
    if use_saved_index and os.path.exists(INDEX_PATH):
        print(f"\n  ✅ 从 {INDEX_PATH} 加载已保存的索引...")
        vectorstore = FAISS.load_local(
            INDEX_PATH, 
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        # 创建新索引
        print(f"\n  🔨 创建新索引（这需要一些时间）...")
        vectorstore = FAISS.from_documents(chunks, embeddings)
        
        # 保存索引
        print(f"  💾 保存索引到 {INDEX_PATH}...")
        vectorstore.save_local(INDEX_PATH)
    
    print(f"✅ 索引创建完成\n")
    return vectorstore

# ============================================
# 步骤 4: 创建 RAG 链
# ============================================
def create_rag_chain(vectorstore):
    """创建 RAG 检索链"""
    print("🔗 创建 RAG 链...\n")
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    print(f"  📌 LLM 模型: {LLM_MODEL}")
    print(f"  🌐 Ollama 地址: {OLLAMA_BASE_URL}\n")

    llm = ChatOllama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.3,
        num_predict=256
    )
    
    # Prompt
    prompt = ChatPromptTemplate.from_template("""
你是一个有帮助的AI助手。请根据以下上下文回答用户的问题。
如果上下文中没有相关信息，请说"我不知道"。

上下文：
{context}

问题：{question}

回答：
""")

    # 文档格式化
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # ✅ 正确的 RAG LCEL 写法（关键！！！）
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    print("✅ RAG 链创建完成\n")
    return rag_chain, retriever
# ============================================
# 步骤 5: 交互式查询
# ============================================
def interactive_qa(rag_chain, retriever):
    """交互式问答"""
    print("="*60)
    print("🚀 RAG Demo 启动！（基于本地 Ollama）")
    print("="*60)
    print(f"LLM 模型: {LLM_MODEL}")
    print(f"嵌入模型: {EMBEDDING_MODEL}")
    print(f"Ollama 地址: {OLLAMA_BASE_URL}")
    print("="*60)
    print("输入问题（输入 'quit', 'exit' 或 'q' 退出）\n")
    
    while True:
        query = input("❓ 你: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("\n👋 再见！")
            break
        
        if not query:
            print("⚠️  请输入有效的问题\n")
            continue
        
        try:
            # 执行 RAG 查询
            print("\n⏳ 处理中...")
            
            # 显示检索的文档
            print("\n📚 检索到的相关文档：")
            retrieved_docs = retriever.invoke(query)
            for i, doc in enumerate(retrieved_docs, 1):
                content_preview = doc.page_content[:150].replace("\n", " ")
                print(f"   {i}. {content_preview}...")
            
            # 生成答案
            print("\n🤖 AI 回答：")
            answer = rag_chain.invoke(query)
            print(f"{answer}\n")

            # for chunk in rag_chain.stream(query):
            #     print(chunk, end="", flush=True)

        except Exception as e:
            print(f"\n❌ 出错了: {e}\n")

# ============================================
# 步骤 6: 批量查询（测试）
# ============================================
def batch_qa(rag_chain):
    """批量查询（用于测试）"""
    test_questions = [
        "Agent 是什么？",
        "RAG 的优点有哪些？",
        "LangChain 的主要功能是什么？"
    ]
    
    print("\n" + "="*60)
    print("📊 批量查询测试")
    print("="*60 + "\n")
    
    for i, question in enumerate(test_questions, 1):
        print(f"问题 {i}: {question}")
        try:
            answer = rag_chain.invoke(question)
            print(f"回答: {answer}\n")
        except Exception as e:
            print(f"❌ 错误: {e}\n")

# ============================================
# 主程序
# ============================================
def main():
    print("🎯 LangChain RAG Demo (本地 Ollama)\n")
    
    # 检查 Ollama 连接
    print("🔍 检查 Ollama 连接...")
    try:
        test_llm = ChatOllama(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL
        )
        test = test_llm.invoke("你好呀")
        print("DEBUG:", test)
        print("CONTENT:", repr(test.content))
        print(f"✅ Ollama 连接成功！\n")
    except Exception as e:
        print(f"""
❌ 无法连接到 Ollama！
错误: {e}

请确保：
1. Ollama 已安装：https://ollama.ai
2. Ollama 服务正在运行（打开命令行运行 'ollama serve'）
3. 已拉取所需模型：
   - ollama pull {LLM_MODEL}
   - ollama pull {EMBEDDING_MODEL}
4. Ollama 地址正确：{OLLAMA_BASE_URL}
""")
        return
    
    # 步骤 1-3: 加载、分割、索引
    docs = load_documents()
    chunks = split_documents(docs)
    vectorstore = create_vectorstore(chunks, use_saved_index=False)
    
    # 步骤 4: 创建 RAG 链
    rag_chain, retriever = create_rag_chain(vectorstore)
    
    # 步骤 5: 交互查询ni
    interactive_qa(rag_chain, retriever)
    
    # 可选：批量查询
    # batch_qa(rag_chain)

if __name__ == "__main__":
    main()