import os
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any, TypedDict, Optional

CHAT_COMPLETIONS_API_KEY = os.getenv("CHAT_COMPLETIONS_API_KEY")
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

def get_llm():
    """统一创建 LLM，方便后续替换模型。"""
    return ChatOpenAI(
        api_key=CHAT_COMPLETIONS_API_KEY,
        base_url=DASHSCOPE_BASE_URL,
        model="deepseek-v4-pro",
        temperature=0,
    )

# 定义状态类型
class AssistantInfo(TypedDict):
    assistant_type: str
    assistant_instructions: str
    user_question: str

class SearchQuery(TypedDict):
    search_query: str
    user_question: str

class SearchResult(TypedDict):
    result_url: str
    search_query: str
    user_question: str
    is_fallback: Optional[bool]

class SearchSummary(TypedDict):
    summary: str
    result_url: str
    user_question: str
    is_fallback: Optional[bool]

class ResearchReport(TypedDict):
    report: str


# 定义统一状态对象
class ResearchState(TypedDict):
    user_question: str # 问题
    assistant_info: Optional[AssistantInfo] # 研究助手类型和研究指令
    search_queries: Optional[List[SearchQuery]] # 当前轮生成的搜索请求
    search_results: Optional[List[SearchResult]] # 网页搜索得到的链接
    search_summaries: Optional[List[SearchSummary]] # 单个网页的总结
    research_summary: Optional[str] # 所有网页摘要合并后的研究上下文
    final_report: Optional[str] # 最后生成的研究报告
    used_fallback_search: Optional[bool] # 是否触发了备用搜索机制
    relevance_evaluation: Optional[Dict[str, Any]] # 相关性评估结果
    should_regenerate_queries: Optional[bool] # 是否需要重新生成搜索词
    iteration_count: Optional[int] # 循环次数
