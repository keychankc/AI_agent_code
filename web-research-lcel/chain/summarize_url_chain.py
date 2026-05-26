from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel

from llm_models import get_llm
from prompts import SUMMARY_PROMPT_TEMPLATE
from web_scraping import web_scrape

RESULT_TEXT_MAX_CHARACTERS = 10000

def prepare_summary_data(x):
    text = web_scrape(x["result_url"])

    return {
        "search_result_text": text[:RESULT_TEXT_MAX_CHARACTERS],
        "result_url": x["result_url"],
        "search_query": x["search_query"],
        "user_question": x["user_question"],
    }

def format_summary_result(x):
    return {
        "summary": (
            f"来源 URL: {x['result_url']}\n"
            f"摘要: {x['text_summary']}"
        ),
        "user_question": x["user_question"],
    }

# 网页抓取与摘要链：
# 输入单个 URL 对象，先抓取网页正文并进行长度截断，
# 再使用 RunnableParallel 一边调用模型生成网页摘要，
# 一边保留原始 URL 和 user_question，
# 最终整理成“来源 + 摘要”的统一结构，供后续多网页摘要合并使用
search_result_text_and_summary_chain = (
    RunnableLambda(prepare_summary_data)
    | RunnableParallel({
        "text_summary": (
            SUMMARY_PROMPT_TEMPLATE
            | get_llm()
            | StrOutputParser()
        ),
        "result_url": lambda x: x["result_url"],
        "user_question": lambda x: x["user_question"],
    })
    | RunnableLambda(format_summary_result)
)