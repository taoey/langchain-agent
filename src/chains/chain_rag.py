# rag_demo.py

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader,TextLoader

# ========== 1. 初始化模型 ==========
llm = ChatOllama(
    model="qwen3:1.7b",
    base_url="http://192.168.3.25:11434",
    temperature=0.7
)

# ========== 2. 加载文档 ==========
# loader = TextLoader("data.txt", encoding="utf-8")
loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
documents = loader.load()

# ========== 3. 文本切分 ==========
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
docs = text_splitter.split_documents(documents)

# ========== 4. 向量化 ==========
embeddings = OllamaEmbeddings(
    model="qwen3-embedding:4b",
    base_url="http://192.168.3.25:11434"
)

# ========== 5. 向量数据库 ==========
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
)

# ========== 6. 检索器 ==========
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3}
)


# ========== 7. RAG 核心 ==========
def rag_query(question: str):
    # 1. 检索
    retrieved_docs = retriever.invoke(question)

    # 2. 拼接上下文
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    print("debug:上下文",context)
    # 3. Prompt（很关键）
    prompt = f"""
    你是一AI助手，请参考提供的上下文回答问题。

    【上下文】
    {context}

    【问题】
    {question}

"""

    # 4. 调用 LLM
    response = llm.invoke(prompt)
    return response.content


# ========== 8. 测试 ==========
if __name__ == "__main__":
    while True:
        q = input("\n请输入问题：")
        if q.lower() in ["exit", "quit"]:
            break

        answer = rag_query(q)
        print("\n回答：", answer)