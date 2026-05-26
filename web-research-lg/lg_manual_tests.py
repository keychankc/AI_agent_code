from agents.assistant_selector import select_assistant
from agents.web_researcher import (
    evaluate_search_relevance,
    generate_search_queries,
    perform_web_searches,
    summarize_search_results,
)


def test_evaluate_search_relevance():
    state = {
        "user_question": "当前英伟达股票还值得买入吗？",
        "search_summaries": [
            {
                "summary": "来源 URL：https://example.com/nvidia-earnings\n摘要：英伟达数据中心业务收入持续增长，AI 芯片需求、毛利率和未来业绩指引是影响股价的重要因素。",
                "result_url": "https://example.com/nvidia-earnings",
                "user_question": "当前英伟达股票还值得买入吗？",
                "is_fallback": False
            },
            {
                "summary": "来源 URL：https://example.com/nvidia-valuation\n摘要：英伟达估值需要结合收入增速、利润率、AI 资本开支周期、竞争格局和市场预期变化进行判断。",
                "result_url": "https://example.com/nvidia-valuation",
                "user_question": "当前英伟达股票还值得买入吗？",
                "is_fallback": False
            },
            {
                "summary": "来源 URL：https://example.com/gpu-history\n摘要：GPU 最初主要用于图形渲染，后来逐步扩展到并行计算、深度学习训练和推理等场景。",
                "result_url": "https://example.com/gpu-history",
                "user_question": "当前英伟达股票还值得买入吗？",
                "is_fallback": False
            }
        ],
        "research_summary": """
            来源 URL：https://example.com/nvidia-earnings
            摘要：英伟达数据中心业务收入持续增长，AI 芯片需求、毛利率和未来业绩指引是影响股价的重要因素。

            来源 URL：https://example.com/nvidia-valuation
            摘要：英伟达估值需要结合收入增速、利润率、AI 资本开支周期、竞争格局和市场预期变化进行判断。

            来源 URL：https://example.com/gpu-history
            摘要：GPU 最初主要用于图形渲染，后来逐步扩展到并行计算、深度学习训练和推理等场景。
        """,
        "used_fallback_search": False
    }
    result = evaluate_search_relevance(state)
    print(result)
    # {
    #     'relevance_evaluation':
    #     {
    #         'relevance_percentage': 66.67,
    #         'explanation': '前两条摘要可直接支持英伟达股票买入决策分析，第三条主要是 GPU 技术背景，相关性较弱。',
    #         'relevant_count': 2,
    #         'total_count': 3
    #     },
    #     'should_regenerate_queries': False
    # }


def test_summarize_search_results():
    state = {
        "search_results": [
            {
                "result_url": "https://www.nvidia.com/en-us/about-nvidia/investor-relations/",
                "search_query": "英伟达 股票 业绩 数据中心 AI 芯片 增长 最新分析",
                "user_question": "当前英伟达股票还值得买入吗？",
                "is_fallback": False
            },
            {
                "result_url": "https://en.wikipedia.org/wiki/Nvidia",
                "search_query": "英伟达 估值 风险 竞争 AI 资本开支",
                "user_question": "当前英伟达股票还值得买入吗？",
                "is_fallback": True
            }
        ],
        "used_fallback_search": True
    }
    result = summarize_search_results(state)
    print(result)
    # {
    #     'search_summaries': [
    #         {
    #             'summary': '来源 URL：...\n摘要：...',
    #             'result_url': 'https://www.nvidia.com/en-us/about-nvidia/investor-relations/',
    #             'user_question': '当前英伟达股票还值得买入吗？',
    #             'is_fallback': False
    #         },
    #         {
    #             'summary': '来源 URL：...\n摘要：...\n[说明：这部分信息来自降级资料源，可能无法直接对应原问题。]',
    #             'result_url': 'https://en.wikipedia.org/wiki/Nvidia',
    #             'user_question': '当前英伟达股票还值得买入吗？',
    #             'is_fallback': True
    #         }
    #     ],
    #     'research_summary': '...',
    #     'used_fallback_search': True
    # }


def test_perform_web_searches():
    states = {
        "search_queries": [
            {"search_query": "英伟达 股票 业绩 数据中心 AI 芯片 增长 最新分析", "user_question": "当前英伟达股票还值得买入吗？"},
            {"search_query": "英伟达 估值 市盈率 收入增速 毛利率 机构观点", "user_question": "当前英伟达股票还值得买入吗？"},
            {"search_query": "英伟达 竞争风险 AI 资本开支 半导体周期 出口管制", "user_question": "当前英伟达股票还值得买入吗？"}
        ],
        "relevance_evaluation": None,
        "should_regenerate_queries": None
    }
    result = perform_web_searches(states)
    print(result)
    # {'search_results': [
    #   {
    #       'result_url': 'https://www.nvidia.com/en-us/about-nvidia/investor-relations/',
    #       'search_query': '英伟达 股票 业绩 数据中心 AI 芯片 增长 最新分析',
    #       'user_question': '当前英伟达股票还值得买入吗？',
    #       'is_fallback': False
    #   },
    #   {
    #       'result_url': 'https://finance.yahoo.com/quote/NVDA/',
    #       'search_query': '英伟达 股票 业绩 数据中心 AI 芯片 增长 最新分析',
    #       'user_question': '当前英伟达股票还值得买入吗？',
    #       'is_fallback': False
    #    }, ...
    #  ],
    #  'used_fallback_search': True}


def test_generate_search_queries():
    states = {
        "assistant_info":
        {
            "assistant_type": "金融分析助手",
            "assistant_instructions": "你是一名资深金融分析 AI 助手。你的核心目标是基于提供的数据和趋势，撰写全面、深入、客观、结构清晰的金融研究报告。",
            "user_question": "当前英伟达股票还值得买入吗？"
        },
        "iteration_count": 2
    }
    result = generate_search_queries(states)
    print(result)
    # {
    #     'search_queries': [
    #         {'search_query': '英伟达 股票 业绩 数据中心 AI 芯片 增长 最新分析', 'user_question': '当前英伟达股票还值得买入吗？'},
    #         {'search_query': '英伟达 估值 市盈率 收入增速 毛利率 机构观点', 'user_question': '当前英伟达股票还值得买入吗？'},
    #         {'search_query': '英伟达 竞争风险 AI 资本开支 半导体周期 出口管制', 'user_question': '当前英伟达股票还值得买入吗？'}
    #     ],
    #     'relevance_evaluation': None,
    #     'should_regenerate_queries': None
    # }


def test_select_assistant():
    state = {
        "user_question": "当前英伟达股票还值得买入吗？"
    }
    result = select_assistant(state)
    print(result)
    # {
    #     'assistant_info':
    #      {
    #         'assistant_type': '金融分析助手',
    #         'assistant_instructions': '你是一名资深金融分析 AI 助手。你的核心目标是基于提供的数据和趋势，撰写全面、深入、客观、结构清晰的金融研究报告。',
    #         'user_question': '当前英伟达股票还值得买入吗？'
    #      }
    # }
