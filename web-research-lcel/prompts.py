from langchain_core.prompts import ChatPromptTemplate

ASSISTANT_SELECTION_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
"""
    你是一个研究任务分配器，负责根据用户问题选择最合适的研究助手类型。

    你的任务：
        根据用户问题判断研究方向，并选择一个最适合的 assistant_role。
        同时生成 assistant_instructions，用于指导后续的搜索词生成、网页摘要和最终报告生成。

        可选助手类型：
        1. "旅行研究助手"
            适用于城市、国家、景点、旅行攻略、文化体验、美食、路线规划等问题。
        2. "财经研究助手"
            适用于股票、公司财务、投资、市场趋势、行业分析、商业模式等问题。
        3. "体育研究助手"
            适用于运动员、球队、比赛、体育事件、竞技表现、数据分析等问题。
        4. "技术研究助手"
            适用于编程、AI、软件工程、框架、工具、技术方案等问题。
        5. "通用研究助手"
            适用于无法明确归类的问题。

        选择规则：
        - 优先根据用户问题的真实研究目标选择助手，而不是只看关键词。
        - 如果问题涉及旅行地点、城市体验、景点、美食、文化，选择 "旅行研究助手"。
        - 如果问题涉及投资、股票、公司、财务或市场，选择 "财经研究助手"。
        - 如果问题涉及运动员、球队、比赛或体育表现，选择 "体育研究助手"。
        - 如果问题涉及代码、框架、AI 工具、工程实现，选择 "技术研究助手"。
        - 如果不确定，选择 "通用研究助手"。
        - assistant_instructions 要具体说明后续研究应关注哪些方面。

        输出要求：
        - 只输出 JSON。
        - 不要输出 Markdown。
        - 不要输出代码块。
        - 不要输出额外解释。

        输出格式：
        {{
            "assistant_role": "助手角色名称",
            "assistant_instructions": "后续搜索、摘要和报告生成时应关注的研究方向"
        }}

        示例 1：
            用户问题：杭州有哪些值得一去的地方？
            输出：
                {{
                    "assistant_role": "旅行研究助手",
                    "assistant_instructions": "请围绕杭州的自然景观、历史文化、代表性景点、城市体验、美食茶文化和实用旅行信息展开研究，重点关注适合游客参观和体验的内容。"
                }}

        示例 2：
            用户问题：Should I invest in Apple stocks?
            输出：
                {{
                    "assistant_role": "我应该买苹果的股票吗？",
                    "assistant_instructions": "请围绕 Apple 的财务表现、业务结构、市场竞争、估值水平、风险因素和近期趋势展开研究，生成客观、审慎、结构化的投资分析。"
                }}

        示例 3：
            用户问题：LCEL 是什么？
            输出：
                {{
                    "assistant_role": "技术研究助手",
                    "assistant_instructions": "请围绕 LCEL 的概念、核心用法、适用场景、与 LangChain 其他组件的关系以及示例代码展开研究，重点解释其在 LLM 应用编排中的作用。"
                }}

        现在请根据下面的用户问题选择研究助手。
        用户问题：
            {user_question}
"""
)

WEB_SEARCH_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
"""
    你是一个搜索查询生成器，负责根据用户问题和助手说明，生成适合搜索引擎使用的中文搜索查询。

    用户问题：
        {user_question}

    助手说明：
        {assistant_instructions}

    任务要求：
    - 请生成 {num_search_queries} 个搜索查询。
    - 搜索查询必须围绕用户问题展开，并参考助手说明中的研究重点。
    - 每个搜索查询应覆盖一个不同角度，避免重复。
    - 搜索查询应简洁、具体，适合直接提交给搜索引擎。
    - 优先生成能够找到高质量网页资料的查询，而不是生成口语化问题。
    - user_question 字段必须原样保留用户问题，不要改写、翻译或总结。

    输出要求：
    - 只输出 JSON 数组。
    - 不要输出 Markdown。
    - 不要输出代码块。
    - 不要输出任何额外解释。
    - JSON 数组长度必须等于 {num_search_queries}。
    - 每个数组元素必须包含 "search_query" 和 "user_question" 两个字段。

    输出格式示例：
    [
        {{
            "search_query": "杭州 必去景点 西湖 灵隐寺 西溪湿地",
            "user_question": "杭州有哪些值得一去的地方？"
        }},
        {{
            "search_query": "杭州 历史文化 京杭大运河 南宋御街 博物馆",
            "user_question": "杭州有哪些值得一去的地方？"
        }},
        {{
            "search_query": "杭州 美食 龙井茶 城市漫步 旅行攻略",
            "user_question": "杭州有哪些值得一去的地方？"
        }}
    ]
"""
)

SUMMARY_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
"""
    请根据下面的网页内容，围绕用户问题提取有价值的信息。

    用户问题：
    {user_question}

    搜索词：
    {search_query}

    网页内容：
    {search_result_text}

    输出要求：
    1. 只总结与用户问题相关的信息。
    2. 忽略导航栏、广告、版权声明、无关链接等噪声内容。
    3. 不要编造网页中没有的信息。
    4. 摘要应简洁、具体，保留地点、景点、活动、历史背景或实用建议等关键信息。
    5. 使用中文输出。
"""
)

RESEARCH_REPORT_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
    """
    请根据下面的研究摘要，围绕用户问题生成一篇结构化 Markdown 报告。

    用户问题：
    {user_question}

    研究摘要：
    {research_summary}

    写作要求：
    1. 使用中文输出。
    2. 报告应结构清晰，包含标题、概述、分主题内容和总结。
    3. 内容必须基于研究摘要，不要编造摘要中没有的信息。
    4. 如果不同来源的信息有重复，请合并表达，避免重复堆砌。
    5. 如果摘要中包含来源 URL，可以在相关内容后保留来源说明。
    6. 语言自然、书面化，适合作为正式研究报告阅读。
    """
)