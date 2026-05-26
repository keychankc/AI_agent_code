from typing import List

def web_search(web_query: str, num_results: int) -> List[str]:
    """根据搜索词返回网页 URL 列表。"""
    from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

    results = DuckDuckGoSearchAPIWrapper().results(
        web_query,
        num_results
    )

    return [result["link"] for result in results]
