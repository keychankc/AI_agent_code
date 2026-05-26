from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser

from llm_models import get_llm
from chain.assistant_chain import assistant_instructions_chain
from chain.search_query_chain import web_searches_chain
from chain.search_url_chain import search_result_urls_chain
from chain.summarize_url_chain import search_result_text_and_summary_chain
from prompts import RESEARCH_REPORT_PROMPT_TEMPLATE

def merge_valid_summaries(items):
    valid_items = [
        item
        for item in items
        if "无法获取网页内容" not in item["summary"]
    ]
    return {
        "summary": "\n".join(
            item["summary"]
            for item in valid_items
        ),
        "user_question":
            valid_items[0]["user_question"]
            if valid_items else ""
    }

search_and_summarization_chain = (
    search_result_urls_chain
    | search_result_text_and_summary_chain.map()
    | RunnableLambda(merge_valid_summaries)
)

merge_research_summaries = RunnableLambda(lambda x: {
    "research_summary": "\n\n".join([item["summary"] for item in x]),
    "user_question": x[0]["user_question"] if len(x) > 0 else "",
})

# 完整研究报告链
web_research_chain = (
    assistant_instructions_chain
    | web_searches_chain
    | search_and_summarization_chain.map()
    | merge_research_summaries
    | RESEARCH_REPORT_PROMPT_TEMPLATE
    | get_llm()
    | StrOutputParser()
)
