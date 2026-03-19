# 测试通过
# rag_demo.py - 终极修复版（解决 Chroma + Ollama 兼容问题）
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# ========== 初始化（不变）=========
llm = ChatOllama(model="qwen3:1.7b", base_url="http://192.168.3.25:11434", temperature=0.1)

loader = TextLoader("data.txt", encoding="utf-8")
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
docs = text_splitter.split_documents(documents)

embeddings = OllamaEmbeddings(model="qwen3-embedding:4b", base_url="http://192.168.3.25:11434")

vectorstore = Chroma.from_documents(docs, embeddings, persist_directory="./chroma_db")
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

def format_docs(docs):
    return "\n\n".join([f"【来源 {i+1}】\n{doc.page_content}" for i, doc in enumerate(docs)])

prompt = ChatPromptTemplate.from_template("""
基于以下上下文回答问题。如果上下文不足，请说明。

上下文：
{context}

问题：{question}

答案：
""")

# ========== 🔥 关键修复：自定义字符串检索器 ==========
def string_retriever(inputs):
    """确保只传递字符串给检索器，避免字典问题"""
    if isinstance(inputs, dict):
        question = inputs["question"]
    else:
        question = inputs
    return retriever.invoke(question)

# 包装成 Runnable，确保输入正确
string_retriever_runnable = RunnableLambda(string_retriever)

# ========== RAG 链 ==========
rag_chain = (
    {
        "context": string_retriever_runnable | format_docs,  # ✅ 修复检索器
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)

print("✅ RAG 修复完成！")

# ========== 测试函数 ==========
def rag_query(question: str) -> str:
    try:
        print(f"\n🔍 '{question}'")

        # 直接输出
        response = rag_chain.invoke(question)  # 直接传字符串！
        return response
        # 流式输出
        for chunk in rag_chain.stream(question):
                print(chunk, end="", flush=True)
    except Exception as e:
        print(f"❌ {e}")
        return f"错误: {str(e)}"

if __name__ == "__main__":
    while True:
        q = input("\n问题: ").strip()
        if q.lower() in ["exit", "quit"]:
            break
        print(f"\n💬 {rag_query(q)}\n")