from typing import Any, Dict, List

from langchain_core.runnables import RunnableLambda

from web_searching import web_search

NUM_SEARCH_RESULTS = 3

# URL 搜索链：
# 输入单个搜索词对象，调用 web_search 获取多个网页 URL。
# 然后把每个 URL 包装成统一结构，保留 result_url、search_query 和 user_question。
search_result_urls_chain = (
    RunnableLambda(lambda x: [
        {
            "result_url": url,
            "search_query": x["search_query"],
            "user_question": x["user_question"],
        }
        for url in web_search(
            web_query=x["search_query"],
            num_results=NUM_SEARCH_RESULTS
        )
    ])
)

# 批量 URL 搜索链：
# search_result_urls_chain 一次只处理一个搜索词对象。
# .map() 会把它应用到搜索词列表中的每个元素上。
all_search_result_urls_chain = search_result_urls_chain.map()


def deduplicate_urls(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    deduped = []

    for item in items:
        url = item["result_url"]

        if url not in seen:
            seen.add(url)
            deduped.append(item)

    return deduped


def flatten_and_deduplicate(
    nested_items: List[List[Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    seen = set()
    deduped = []

    for group in nested_items:
        for item in group:
            url = item["result_url"]

            if url not in seen:
                seen.add(url)
                deduped.append(item)

    return deduped