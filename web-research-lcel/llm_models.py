import os
from langchain_openai import ChatOpenAI

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