from models import get_llm
from prompts import RESEARCH_REPORT_PROMPT_TEMPLATE
from typing import Dict, Any


def write_research_report(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据汇总后的搜索结果生成研究报告。
    """

    research_summary = state["research_summary"]
    user_question = state["user_question"]

    # 格式化 Prompt
    prompt = RESEARCH_REPORT_PROMPT_TEMPLATE.format(
        research_summary=research_summary,
        user_question=user_question
    )

    # 获取大模型生成结果
    llm = get_llm()
    response = llm.invoke(prompt)
    report = response.content

    # 返回更新后的状态
    return { "final_report": report }