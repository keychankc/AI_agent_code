from models import get_llm, AssistantInfo
from prompts import ASSISTANT_SELECTION_PROMPT_TEMPLATE
from langchain_core.output_parsers import StrOutputParser
import json
from typing import Dict, Any


def select_assistant(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据用户问题选择合适的研究助手。
    """

    user_question = state["user_question"]

    # 组装prompt
    prompt = ASSISTANT_SELECTION_PROMPT_TEMPLATE.format(
        user_question=user_question
    )

    # 调用模型
    llm = get_llm()
    response = llm.invoke(prompt)
    response_text = response.content

    try:
        # 提取响应中的 JSON 部分
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        json_str = response_text[json_start:json_end]

        # 解析 JSON
        assistant_info = json.loads(json_str)

        # 返回更新后的状态对象
        return {
            "assistant_info": assistant_info
        }

    except Exception as e:
        # 如果解析失败，默认通用研究助手
        default_assistant = {
            "assistant_type": "通用研究助手",
            "assistant_instructions": (
                "你是一名具备通用研究能力的 AI 助手。"
                "你的目标是基于已有信息，围绕目标问题输出全面、深入、客观、结构清晰的研究报告。"
                "优先关注事实依据、逻辑完整性和信息相关性，避免主观推断。"
            ),
            "user_question": user_question
        }
        return {
            "assistant_info": default_assistant
        }