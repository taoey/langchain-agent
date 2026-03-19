from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 模型
llm = ChatOllama(
    model="qwen3:1.7b",
    base_url="http://192.168.3.25:11434"
)
# Prompt 模板
prompt = ChatPromptTemplate.from_template(
    "请用简单易懂的语言解释：{topic}"
)
# 链（LCEL 写法）
chain = prompt | llm | StrOutputParser()

# 调用
result = chain.invoke({"topic": "什么是向量数据库"})

print(result)