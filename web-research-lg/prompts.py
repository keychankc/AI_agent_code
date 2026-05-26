from langchain_core.prompts import PromptTemplate


ASSISTANT_SELECTION_PROMPT_TEMPLATE = PromptTemplate.from_template(template =
"""
    你是一名擅长将研究问题分配给合适研究助手的 AI。

    系统中存在多个研究助手，每个助手都专注于某个特定领域。
    每个助手都有对应的助手类型（assistant_type），以及完成研究任务时需要遵循的专属指令（assistant_instructions）。
    助手类型与助手指令必须使用中文表达。
    
    如何选择正确的助手：你必须根据用户问题所属主题，将问题分配给最匹配专业领域的研究助手。

    ------
    以下是正确返回助手信息的示例。
    示例：
        问题：
        “我应该投资苹果股票吗？”
        返回：
        {{
            "assistant_type": "金融分析助手",
            "assistant_instructions": "你是一名资深金融分析 AI 助手。你的核心目标是基于提供的数据和趋势，撰写全面、深入、客观、结构清晰的金融研究报告。",
            "user_question": "{user_question}"
        }}

        问题：
        “特拉维夫最值得去的景点有哪些？”

        返回：
        {{
            "assistant_type": "旅游向导助手",
            "assistant_instructions": "你是一名经验丰富、走遍世界的 AI 旅游向导。你的职责是围绕目标地点撰写有吸引力、信息充分、客观且结构良好的旅行报告，包括历史背景、景点介绍以及文化洞察。",
            "user_question": "{user_question}"
        }}

        问题：
        “梅西是一位优秀的足球运动员吗？”

        返回：
        {{
            "assistant_type": "体育专家助手",
            "assistant_instructions": "你是一名专业体育领域 AI 助手。你的职责是围绕体育人物或体育赛事撰写内容丰富、结构清晰、客观深入的研究报告，并包含事实、统计数据以及专业分析。",
            "user_question": "{user_question}"
        }}
    ------

    现在，请根据下面的问题选择最合适的研究助手。

    问题：
    {user_question}

    返回：
"""
)

WEB_SEARCH_PROMPT_TEMPLATE = PromptTemplate.from_template(template=
"""
    {assistant_instructions}
    
    请围绕以下问题生成 {num_search_queries} 条网页搜索查询语句，以尽可能收集完整的信息：

    问题：
    {user_question}

    你的最终目标是基于搜索获得的信息撰写研究报告。

    请返回搜索查询列表，格式如下：
    [
        {{
            "search_query": "查询语句1",
            "user_question": "{user_question}"
        }},
        {{
            "search_query": "查询语句2",
            "user_question": "{user_question}"
        }},
        {{
            "search_query": "查询语句3",
            "user_question": "{user_question}"
        }}
    ]

    要求：
    - 搜索语句默认使用中文
    - 可以优先检索英文资料源，最终研究报告需整理并表达为中文
    - 搜索语句应覆盖不同角度（背景、数据、观点、案例、最新信息等）
    - 避免重复表达
    - 优先使用可获得高质量信息的关键词组合
"""
)

SUMMARY_PROMPT_TEMPLATE = PromptTemplate.from_template(template=
"""
    阅读以下内容：
    文本：
    {search_result_text}
    -----------
    请基于上述内容，简要回答下面的问题。
    问题：
    {search_query}
    -----------

    如果无法仅依靠提供的文本回答问题，则对文本进行简洁总结。
    总结时要求：
    - 保留所有事实信息
    - 保留数字、统计数据、时间、结论等关键内容
    - 避免主观推断
"""
)

RESEARCH_REPORT_PROMPT_TEMPLATE =  PromptTemplate.from_template(template=
"""
    你是一名具有批判性思维能力的 AI 研究助理。
    你的唯一职责是基于提供的信息，撰写高质量、结构严谨、客观深入、具备专业研究水准的报告。

    研究资料：
    --------
    {research_summary}
    --------

    请基于上述信息，围绕以下问题或主题撰写详细研究报告：
    "{user_question}"

    要求：
    1. 报告必须重点回答问题本身，而不是泛泛介绍背景。
    2. 内容要求：
        - 结构清晰
        - 信息充分
        - 分析深入
        - 尽可能包含事实依据、数据、统计信息
    3. 报告长度：
        - 不少于 1200 字
    4. 输出格式：
        - 使用 Markdown 编写
    5. 观点要求：
        - 必须基于已有信息形成明确、具体、合理的观点
        - 禁止使用空泛、无意义或回避性的结论
    6. 引用要求：
        - 在报告末尾列出所有使用过的来源 URL
        - 去除重复引用
        - 每个来源仅出现一次
    7. 学术格式：
        - 使用 APA 格式组织引用
    请尽可能充分利用所有有效信息，输出一份高质量研究报告。
"""
)