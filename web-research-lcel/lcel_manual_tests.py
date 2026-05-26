import json

from chain.assistant_chain import assistant_instructions_chain
from chain.research_chain import search_and_summarization_chain
from chain.search_query_chain import web_searches_chain
from chain.search_url_chain import (
    all_search_result_urls_chain,
    flatten_and_deduplicate,
    search_result_urls_chain,
)
from chain.summarize_url_chain import search_result_text_and_summary_chain


def test_generate_assistant_instructions():
    result = assistant_instructions_chain.invoke({
        "user_question": "杭州有哪些值得一去的地方？"
    })
    print(result)
    # {
    #     "user_question": "杭州有哪些值得一去的地方？",
    #     "assistant_role": "旅行研究助手",
    #     "assistant_instructions": "请围绕杭州的自然景观、历史文化、代表性景点、城市体验、美食茶文化和实用旅行信息展开研究，重点关注适合游客参观和体验的内容。"
    # }


def test_generate_search_instructions():
    input_data = {
        "user_question": "杭州有哪些值得一去的地方？",
        "assistant_role": "旅行研究助手",
        "assistant_instructions": "请围绕杭州的自然景观、历史文化、代表性景点、城市体验、美食茶文化和实用旅行信息展开研究，重点关注适合游客参观和体验的内容。"
    }

    search_queries = web_searches_chain.invoke(input_data)

    print(search_queries)
    # [
    #     {'search_query': '杭州 必去景点 西湖 灵隐寺 西溪湿地 推荐', 'user_question': '杭州有哪些值得一去的地方？'},
    #     {'search_query': '杭州 历史文化街区 南宋御街 京杭大运河 博物馆 游玩攻略','user_question': '杭州有哪些值得一去的地方？'},
    #     {'search_query': '杭州 龙井茶 美食 茶馆 城市漫步 行程建议', 'user_question': '杭州有哪些值得一去的地方？'}
    # ]


def test_generate_search_result_urls_instructions():
    input_data = {
        'search_query': '杭州 必去景点 西湖 灵隐寺 西溪湿地 推荐',
        'user_question': '杭州有哪些值得一去的地方？'
    }

    urls = search_result_urls_chain.invoke(input_data)

    print(urls)
    # [
    #  {'result_url': 'https://www.klook.com/zh-CN/activity/155336-private-guide-1-day-tour-of-hangzhou-city-by-car/', 'search_query': '杭州 必去景点 西湖 灵隐寺 西溪湿地 推荐', 'user_question': '杭州有哪些值得一去的地方？'},
    #  {'result_url': 'https://www.getyourguide.com/zh-cn/lingyin-temple-l150150/', 'search_query': '杭州 必去景点 西湖 灵隐寺 西溪湿地 推荐', 'user_question': '杭州有哪些值得一去的地方？'},
    #  {'result_url': 'https://www.getyourguide.com/zh-cn/hangzhou-l1241/guided-tours-tc1144/', 'search_query': '杭州 必去景点 西湖 灵隐寺 西溪湿地 推荐', 'user_question': '杭州有哪些值得一去的地方？'}
    # ]


def test_generate_multiple_search_queries():
    search_queries = [
        {
            "search_query": "杭州 必去景点 西湖 灵隐寺 西溪湿地",
            "user_question": "杭州有哪些值得一去的地方？"
        },
        {
            "search_query": "杭州 历史文化 京杭大运河 南宋御街 博物馆",
            "user_question": "杭州有哪些值得一去的地方？"
        },
        {
            "search_query": "杭州 美食 龙井茶 城市漫步 旅行攻略",
            "user_question": "杭州有哪些值得一去的地方？"
        }
    ]
    nested_urls = all_search_result_urls_chain.invoke(search_queries)
    print("多个搜索词返回结果，嵌套列表：")
    print(json.dumps(nested_urls, ensure_ascii=False, indent=2))
    deduped_urls = flatten_and_deduplicate(nested_urls)
    print("展开并去重后的 URL 列表：")
    print(json.dumps(deduped_urls, ensure_ascii=False, indent=2))
    # [
    #     {
    #         "result_url": "https://www.sohu.com/a/953786156_120932760",
    #         "search_query": "杭州 必去景点 西湖 灵隐寺 西溪湿地",
    #         "user_question": "杭州有哪些值得一去的地方？"
    #     },
    #     {
    #         "result_url": "https://news.qq.com/rain/a/20260305A04ETV00",
    #         "search_query": "杭州 必去景点 西湖 灵隐寺 西溪湿地",
    #         "user_question": "杭州有哪些值得一去的地方？"
    #     },...
    # ]


def test_generate_search_result_text_and_summary():
    input_data = {
        "result_url": "https://www.sohu.com/a/953786156_120932760",
        "search_query": "杭州 必去景点 西湖 灵隐寺 西溪湿地",
        "user_question": "杭州有哪些值得一去的地方？"
    }
    result = search_result_text_and_summary_chain.invoke(input_data)
    print(result)
    # {
    #     'summary': '来源 URL: https://www.sohu.com/a/953786156_120932760\n摘要: xxx',
    #     'user_question': '杭州有哪些值得一去的地方？'
    # }


def test_generate_search_and_summarization():
    input_data = {
        "search_query": "杭州 必去景点 西湖 灵隐寺 西溪湿地",
        "user_question": "杭州有哪些值得一去的地方？"
    }
    result = search_and_summarization_chain.invoke(input_data)
    print(result)
