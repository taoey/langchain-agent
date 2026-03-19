"""
意图分类器 - 测试用例整理
用于对银行客服用户的查询进行分类，支持：query_balance(余额查询), transfer(转账), human(人工客服/投诉/不满), other(其他)
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


# 定义意图分类的 Pydantic 模型
class Intent(BaseModel):
    """用户查询的意图分类"""
    intent: str = Field(..., description="意图类别：'query_balance' 查询余额，'transfer' 转账，'human' 人工客服/投诉/不满，'other' 其他")
    confidence: float = Field(..., description="置信度 (0.0-1.0)")
    reason: str = Field(..., description="分类理由")


# 初始化 LLM
llm = ChatOllama(model="qwen3:1.7b", base_url="http://192.168.3.25:11434", temperature=0)


# 创建带结构化输出的 LLM
intent_classifier = llm.with_structured_output(Intent)

# 定义聊天提示
prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个银行客服意图分类器。
支持的意图：query_balance (余额查询), transfer (转账), human (人工客服/投诉/不满), other (其他)。
只返回结构化 JSON，不要添加额外文本。"""),
    ("human", "{query}")
])

chain = prompt | intent_classifier


class TestResult:
    """测试结果类"""
    def __init__(self, input_query: str, expected_intent: str, min_confidence: float = 0.7):
        self.input_query = input_query
        self.expected_intent = expected_intent
        self.min_confidence = min_confidence
    
    def get_status(self, result: Intent) -> str:
        status = "PASS" if result.intent == self.expected_intent else "FAIL"
        confidence_match = result.confidence >= self.min_confidence
        return status
    
    def __repr__(self):
        return f"TestQuery({self.input_query!r}, expected: {self.expected_intent})"


class IntentClassifierTest:
    """意图分类器测试类"""
    
    # 测试用例集
    TEST_CASES: List[TestResult] = [
        # 余额查询测试
        TestResult("我的余额是多少？", "query_balance", 0.8),
        TestResult("查询一下我的账户余额", "query_balance", 0.8),
        TestResult("账户里有多少钱", "query_balance", 0.7),
        TestResult("帮我看看余额", "query_balance", 0.7),
        
        # 转账测试
        TestResult("帮我转 100 元给张三", "transfer", 0.8),
        TestResult("转账 500 元到李四的账户", "transfer", 0.8),
        TestResult("把 1000 元转给他", "transfer", 0.7),
        TestResult("给我转钱", "transfer", 0.6),
        
        # 人工客服/投诉/不满测试
        TestResult("什么破系统，转人工!!!", "human", 0.75),
        TestResult("什么破系统，我要投诉！", "human", 0.75),
        TestResult("什么垃圾系统，傻逼玩意！！！", "human", 0.75),
        TestResult("这个系统太差了", "human", 0.7),
        TestResult("我要投诉你们", "human", 0.8),
        TestResult("我要找人工客服", "human", 0.8),
        
        # 其他意图测试
        TestResult("今天天气怎么样？", "other", 0.8),
        TestResult("推荐几部电影", "other", 0.8),
        TestResult("讲个笑话", "other", 0.7),
    ]
    
    def run_tests(self):
        """运行所有测试用例"""
        print("=" * 60)
        print("意图分类器测试套件")
        print("=" * 60)
        
        total = len(self.TEST_CASES)
        passed = 0
        failed = 0
        total_confidence = 0.0
        
        print(f"\n测试用例数量：{total}\n")
        
        for test in self.TEST_CASES:
            result = chain.invoke({"query": test.input_query})
            
            status = test.get_status(result)
            
            if status == "PASS":
                passed += 1
                print(f"✓ {test}")
                print(f"  结果：{result}")
                print(f"  状态：{status}")
            else:
                failed += 1
                print(f"✗ {test}")
                print(f"  预期：{test.expected_intent}")
                print(f"  实际：{result.intent}")
                print(f"  状态：{status}")
            
            print()
        
        # 统计信息
        print("=" * 60)
        print(f"测试结果：{passed}/{total} 通过 ({100*passed/total:.1f}%)")
        print("=" * 60)
        
        return passed == total
    
    def run_single_test(self, test_case: TestResult) -> TestResult:
        """运行单个测试用例"""
        print(f"\n测试：{test_case}")
        result = chain.invoke({"query": test_case.input_query})
        status = test_case.get_status(result)
        return status, result


def run_all_tests():
    """运行所有测试用例"""
    test = IntentClassifierTest()
    return test.run_tests()


if __name__ == "__main__":
    run_all_tests()