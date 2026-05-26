from agents.assistant_selector import select_assistant
from agents.web_researcher import (
    evaluate_search_relevance,
    generate_search_queries,
    perform_web_searches,
    summarize_search_results,
)
from models import ResearchState
from langgraph.graph import StateGraph, END
from typing import Dict, Any
from agents.report_writer import write_research_report


def create_research_graph() -> StateGraph:
    # 定义图
    graph = StateGraph(ResearchState)

    # 向图中添加节点
    graph.add_node("select_assistant", select_assistant)
    graph.add_node("generate_search_queries", generate_search_queries)
    graph.add_node("perform_web_searches", perform_web_searches)
    graph.add_node("summarize_search_results", summarize_search_results)
    graph.add_node("evaluate_search_relevance", evaluate_search_relevance)
    graph.add_node("write_research_report", write_research_report)

    # 定义相关性评估后的条件路由函数
    def route_based_on_relevance(state: Dict[str, Any]) -> str:
        """
        根据相关性评估结果，决定重新生成搜索词或继续撰写报告。
        """
        # 获取当前迭代次数
        iteration_count = state.get("iteration_count", 0)

        # 增加迭代次数
        new_iteration_count = iteration_count + 1

        # 将新的迭代次数写回状态
        state["iteration_count"] = new_iteration_count

        # 如果达到最大迭代次数（3 次），则使用当前结果继续撰写报告
        if new_iteration_count >= 3:
            print(
                f"已达到最大迭代次数（{new_iteration_count}），将使用当前结果继续撰写报告。")
            return "write_research_report"

        # 否则，根据相关性评估结果判断是否需要重新生成搜索词
        if state.get("should_regenerate_queries", False):
            print(f"第 {new_iteration_count} 轮：正在重新生成搜索词。")
            return "generate_search_queries"
        else:
            print(f"第 {new_iteration_count} 轮：搜索结果相关，继续撰写报告。")
            return "write_research_report"

    # 定义图的执行流程
    graph.add_edge("select_assistant", "generate_search_queries")
    graph.add_edge("generate_search_queries", "perform_web_searches")
    graph.add_edge("perform_web_searches", "summarize_search_results")
    graph.add_edge("summarize_search_results", "evaluate_search_relevance")

    # 根据相关性评估结果添加条件路由
    graph.add_conditional_edges(
        "evaluate_search_relevance",
        route_based_on_relevance,
        {
            "generate_search_queries": "generate_search_queries",
            "write_research_report": "write_research_report"
        }
    )

    graph.add_edge("write_research_report", END)

    # 设置入口节点
    graph.set_entry_point("select_assistant")

    return graph


def run_research(question: str) -> str:
    """
    使用用户问题运行研究工作流。
    参数：question用户的研究问题
    返回：最终研究报告
    """
    # 创建图
    research_graph = create_research_graph()

    # 编译图
    app = research_graph.compile()

    # 初始化状态
    initial_state = {
        "user_question": question,
        "assistant_info": None,
        "search_queries": None,
        "search_results": None,
        "search_summaries": None,
        "research_summary": None,
        "final_report": None,
        "used_fallback_search": False,
        "relevance_evaluation": None,
        "should_regenerate_queries": None,
        "iteration_count": 0
    }

    # 运行图
    result = app.invoke(initial_state)

    # 提取并返回最终报告
    return result["final_report"]

if __name__ == "__main__":
    question = "当前英伟达股票还值得买入吗？"
    report = run_research(question)
    print(report)
