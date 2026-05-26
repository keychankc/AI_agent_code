from models import get_llm, SearchQuery, SearchResult, SearchSummary
from prompts import WEB_SEARCH_PROMPT_TEMPLATE, SUMMARY_PROMPT_TEMPLATE
from utils.web_searching import web_search
from utils.web_scraping import web_scrape
import json
from typing import Dict, Any, List

NUM_SEARCH_QUERIES = 3
NUM_SEARCH_RESULTS_PER_QUERY = 3
RESULT_TEXT_MAX_CHARACTERS = 10000


def generate_search_queries(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据研究助手指令和用户问题生成搜索查询。

    为了提升搜索结果质量，会根据当前迭代次数动态调整搜索策略：
    - 第一次：正常生成搜索词
    - 第二次：基于上一轮结果生成更具体的搜索方向
    - 第三次及以后：完全切换搜索角度
    """

    assistant_info = state["assistant_info"]
    user_question = assistant_info["user_question"]
    assistant_instructions = assistant_info["assistant_instructions"]

    # 当前搜索轮次
    iteration_count = state.get("iteration_count", 0)

    # 获取上一轮搜索记录与相关性评估
    previous_queries = state.get("search_queries", [])
    relevance_evaluation = state.get("relevance_evaluation", None)

    # 根据迭代次数生成不同 Prompt
    if iteration_count == 0:
        print("正在生成初始搜索请求...")

        prompt = WEB_SEARCH_PROMPT_TEMPLATE.format(
            assistant_instructions=assistant_instructions,
            user_question=user_question,
            num_search_queries=NUM_SEARCH_QUERIES
        )

    elif iteration_count == 1:
        print("第一次重新搜索，正在生成更精确的搜索方向...")

        previous_query_list = ", ".join([q["search_query"] for q in previous_queries])

        relevance_percentage = (
            relevance_evaluation.get("relevance_percentage", 0)
            if relevance_evaluation
            else 0
        )
        relevance_explanation = (
            relevance_evaluation.get("explanation", "无评估说明")
            if relevance_evaluation
            else ""
        )
        prompt = f"""
                    {assistant_instructions}

                    由于上一轮搜索结果相关性不足，需要重新生成搜索请求。

                    原始问题：
                    {user_question}

                    上一轮搜索请求：
                    {previous_query_list}

                    相关性评估：
                    相关度 {relevance_percentage}%

                    评估说明：
                    {relevance_explanation}

                    请重新生成 {NUM_SEARCH_QUERIES} 条新的网页搜索语句。

                    要求：
                    1. 搜索方向比上一轮更具体、更聚焦
                    2. 不允许重复已有搜索词
                    3. 不允许仅调整措辞
                    4. 必须尝试新的信息获取角度
                    5. 搜索目标仍然围绕原始问题
                    6. 搜索语句默认使用中文
                    7. 可以优先检索英文资料源，最终研究报告需整理并表达为中文

                    返回格式：
                    [
                         {{"search_query":"查询1","user_question":"{user_question}"}},
                         {{"search_query":"查询2","user_question":"{user_question}"}},
                         {{"search_query":"查询3","user_question":"{user_question}"}}
                    ]
                """

    else:
        print(f"第 {iteration_count} 轮搜索，正在切换搜索策略...")

        all_previous_queries = ", ".join([q["search_query"] for q in previous_queries])

        prompt = f"""
                    {assistant_instructions}

                    当前进入最后一次搜索尝试。
                    原始问题：
                    {user_question}
                    以下搜索方向已经尝试但效果不足：

                    {all_previous_queries}

                    请从完全不同的角度重新设计搜索请求，可以考虑：
                    1. 将问题拆成多个更小的问题
                    2. 使用专业术语或领域关键词
                    3. 搜索专家观点或研究报告
                    4. 搜索案例分析或真实实践
                    5. 补充历史背景与发展脉络

                    要求：
                    1. 不允许重复任何历史搜索词
                    2. 不允许简单改写已有搜索语句
                    3. 必须采用新的研究路径
                    4. 搜索结果应尽可能覆盖原问题
                    5. 搜索语句默认使用中文
                    6. 可以优先检索英文资料源，最终研究报告需整理并表达为中文

                    请生成 {NUM_SEARCH_QUERIES} 条全新的搜索请求。
                    返回格式：

                    [
                        {{"search_query":"查询1","user_question":"{user_question}"}},
                        {{"search_query":"查询2","user_question":"{user_question}"}},
                        {{"search_query":"查询3","user_question":"{user_question}"}}
                    ]
                """

    # 调用模型
    llm = get_llm()
    response = llm.invoke(prompt)
    response_text = response.content

    try:
        # 提取返回结果中的 JSON 数组
        json_start = response_text.find("[")
        json_end = response_text.rfind("]") + 1
        json_str = response_text[json_start:json_end]

        # 解析搜索结果
        search_queries = json.loads(json_str)
        print(f"成功生成 {len(search_queries)} 条搜索请求")

        for i, query in enumerate(search_queries):
            print(f"搜索词 {i + 1}：" f"{query['search_query']}")
        return {
            "search_queries": search_queries,
            # 新搜索开始后重置评估状态
            "relevance_evaluation": None,
            "should_regenerate_queries": None
        }
    except Exception as e:
        print(f"解析搜索请求失败：{str(e)}")

        # 降级搜索方案
        default_queries = [
            {
                "search_query": f"{user_question} 第{iteration_count + 1}轮搜索",
                "user_question": user_question
            }
        ]

        print(f"使用默认搜索请求：" f"{default_queries[0]['search_query']}")

        return {
            "search_queries": default_queries,
            "relevance_evaluation": None,
            "should_regenerate_queries": None
        }

def perform_web_searches(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据生成的搜索请求执行网页搜索。
    """
    search_queries = state["search_queries"]
    search_results = []
    fallback_used = False

    print(f"正在执行 {len(search_queries)} 条网页搜索请求...")

    # 遍历每个搜索请求并获取搜索结果
    for query_obj in search_queries:
        search_query = query_obj["search_query"]
        user_question = query_obj["user_question"]

        try:
            # 获取搜索结果
            print(f"正在搜索：{search_query}")
            urls = web_search(
                web_query=search_query,
                num_results=NUM_SEARCH_RESULTS_PER_QUERY
            )

            # 判断是否使用了降级搜索结果（例如 Wikipedia 或通用资料来源）
            if any(
                "wikipedia.org" in url or "baike.baidu.com" in url or "zhihu.com" in url
                for url in urls[:2]
            ):
                print(f"搜索请求触发降级搜索：{search_query}")
                fallback_used = True
                is_fallback = True
            else:
                is_fallback = False

            # 将搜索结果加入结果列表
            for url in urls:
                search_results.append({
                    "result_url": url,
                    "search_query": search_query,
                    "user_question": user_question,
                    "is_fallback": is_fallback
                })

            print(f"搜索请求返回 {len(urls)} 条结果：{search_query}")

        except Exception as e:

            print(f"搜索请求失败：{search_query}，错误：{str(e)}")

            # 即使某个搜索失败，也继续执行其他搜索请求
            continue

    # 如果完全没有搜索结果，则使用默认降级结果
    if not search_results:

        print("没有获得搜索结果，使用通用中文降级信息源。")

        fallback_url = "https://en.wikipedia.org/wiki/Main_Page"

        search_results.append({
            "result_url": fallback_url,
            "search_query": "通用信息",
            "user_question": state["user_question"],
            "is_fallback": True
        })

        fallback_used = True

    # 返回更新后的状态，并记录是否使用了降级搜索
    return {
        "search_results": search_results,
        "used_fallback_search": fallback_used
    }


def summarize_search_results(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    总结搜索结果。
    """
    search_results = state["search_results"]
    used_fallback_search = state.get("used_fallback_search", False)
    llm = get_llm()
    summaries = []

    print(f"正在总结 {len(search_results)} 条搜索结果...")

    # 遍历每条搜索结果，抓取正文并生成摘要
    for result in search_results:
        result_url = result["result_url"]
        search_query = result["search_query"]
        user_question = result["user_question"]
        is_fallback = result.get("is_fallback", False)

        try:
            # 获取网页正文
            print(f"正在抓取网页内容：{result_url}")
            search_result_text = web_scrape(url=result_url)[:RESULT_TEXT_MAX_CHARACTERS]

            # 如果抓取失败或正文过短，则跳过
            if (
                search_result_text.startswith("获取网页失败")
                or len(search_result_text) < 50
            ):
                print(f"跳过 {result_url}：网页抓取失败或正文内容不足")
                continue

            # 组装摘要 Prompt；降级结果需要额外提醒来源可能不完全匹配问题
            if is_fallback:
                prompt = f"""
                你正在总结一条降级资料源的内容。该资料源是在主搜索引擎不可用时使用的，因此它可能无法直接回答问题。

                请阅读以下文本：
                文本：
                {search_result_text} 

                -----------

                请基于上述文本，简要回答下面的问题。
                问题：
                {search_query}

                -----------
                如果无法仅依靠提供的文本回答问题，则对文本进行简洁总结。
                总结时要求：
                - 使用中文输出
                - 保留所有事实信息
                - 保留数字、统计数据、时间、结论等关键内容
                - 避免主观推断

                注意：这是降级资料源，内容可能无法直接对应问题。
                """
            else:
                prompt = SUMMARY_PROMPT_TEMPLATE.format(
                    search_result_text=search_result_text,
                    search_query=search_query
                )

            # 获取摘要
            summary_response = llm.invoke(prompt)
            text_summary = summary_response.content

            # 为降级资料源补充说明
            if is_fallback:
                source_note = "[说明：这部分信息来自降级资料源，可能无法直接对应原问题。]"
                text_summary = f"{text_summary}\n{source_note}"

            # 创建摘要对象
            summary = {
                "summary": f"来源 URL：{result_url}\n摘要：{text_summary}",
                "result_url": result_url,
                "user_question": user_question,
                "is_fallback": is_fallback
            }

            summaries.append(summary)
            print(f"成功总结网页内容：{result_url}")
        except Exception as e:
            print(f"总结网页内容失败：{result_url}，错误：{str(e)}")
            # 单条结果出错时跳过，继续处理其他结果
            continue

    # 创建研究上下文摘要
    if summaries:
        research_summary = "\n\n".join([s["summary"] for s in summaries])
        print(f"已基于 {len(summaries)} 个来源生成研究上下文摘要")

        # 如果使用过降级搜索，则补充说明
        if used_fallback_search:
            fallback_note = "\n\n[说明：由于主搜索引擎不可用，部分或全部信息来自降级资料源，相关性可能低于正常搜索结果。]"
            research_summary += fallback_note
    else:
        research_summary = "未找到相关信息，请尝试使用不同的搜索请求。"
        print("警告：未能从搜索结果生成摘要")

    # 返回更新后的状态
    return {
        "search_summaries": summaries,
        "research_summary": research_summary,
        "used_fallback_search": used_fallback_search
    }


def evaluate_search_relevance(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    评估搜索摘要与原始问题的相关性。
    如果相关摘要少于 50%，则返回搜索词生成环节重新搜索。
    """
    search_summaries = state.get("search_summaries", [])
    user_question = state["user_question"]
    research_summary = state.get("research_summary", "")

    print("正在评估搜索摘要与原始问题的相关性...")

    # 如果没有搜索摘要，则需要重新生成搜索词
    if not search_summaries or not research_summary:
        print("未找到搜索摘要，正在重新生成搜索词...")
        return {"should_regenerate_queries": True}

    # 使用 LLM 评估摘要相关性
    llm = get_llm()

    # 构造相关性评估 Prompt
    evaluation_prompt = f"""
        你是一名专业研究评估员。你的任务是评估搜索结果摘要与原始研究问题的相关性。

        原始研究问题：{user_question}

        搜索结果摘要：{research_summary}

        请逐条判断每个搜索结果摘要是否有助于回答原始问题，并计算相关摘要占全部摘要的百分比。

        判断标准：
        - 如果摘要直接回答了原始问题，或提供了回答问题所需的事实、数据、背景、观点、案例，则视为相关。
        - 如果摘要只包含泛泛背景、与问题主题相近但无法支持回答，或主要内容偏离问题，则视为不相关。
        - 如果内容来自降级资料源，也必须按实际内容判断相关性，不要因为来源是降级资料源就自动判为不相关。

        请只返回一个 JSON 对象，不要添加 Markdown、解释性前后缀或代码块。JSON 结构如下：
        {{
            "relevance_percentage": <相关摘要占比，0 到 100 之间的数字>,
            "explanation": <简要说明你的评估依据>,
            "relevant_count": <相关摘要数量>,
            "total_count": <摘要总数>
        }}
    """

    try:
        # 获取 LLM 评估结果
        evaluation_response = llm.invoke(evaluation_prompt)
        evaluation_text = evaluation_response.content

        # 从模型回复中提取 JSON
        try:
            # 定位 JSON 对象
            json_start = evaluation_text.find('{')
            json_end = evaluation_text.rfind('}') + 1
            json_str = evaluation_text[json_start:json_end]

            # 解析 JSON
            evaluation = json.loads(json_str)
            relevance_percentage = evaluation.get("relevance_percentage", 0)

            # 相关性低于 50% 时重新生成搜索词
            should_regenerate = relevance_percentage < 50

            if should_regenerate:
                print(f"只有 {relevance_percentage}% 的搜索结果相关，正在重新生成搜索词...")
            else:
                print(f"{relevance_percentage}% 的搜索结果相关，继续撰写研究报告...")

            return {
                "relevance_evaluation": evaluation,
                "should_regenerate_queries": should_regenerate
            }
        except Exception as e:
            print(f"解析相关性评估结果失败：{str(e)}")
            # 如果无法解析评估结果，则保守地重新生成搜索词
            return {"should_regenerate_queries": True}
    except Exception as e:
        print(f"相关性评估过程出错：{str(e)}")
        # 如果评估过程出错，则保守地重新生成搜索词
        return {"should_regenerate_queries": True}
