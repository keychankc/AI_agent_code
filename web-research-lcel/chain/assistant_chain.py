from prompts import ASSISTANT_SELECTION_PROMPT_TEMPLATE, WEB_SEARCH_PROMPT_TEMPLATE
from llm_models import get_llm

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from utilities import to_obj

# 角色选择子链 根据用户问题，让模型判断应该使用什么助手角色，并输出结构化 JSON。
assistant_selection_chain = (
    ASSISTANT_SELECTION_PROMPT_TEMPLATE
    | get_llm()
    | StrOutputParser()
    | to_obj
)

# 角色指令链：输入 user_question，先调用角色选择子链，再把结果整理成后续链需要的字段。
assistant_instructions_chain = (
    # 1.保留原始问题，并调用 assistant_selection_chain 生成角色选择结果。
    RunnableLambda(lambda x: {
        "user_question": x["user_question"],
        "assistant_result": assistant_selection_chain.invoke({
            "user_question": x["user_question"]
        })
    })

    # 2.把 assistant_result 中的字段展开，方便后续链直接使用。
    | RunnableLambda(lambda x: {
        "user_question": x["user_question"],
        "assistant_role": x["assistant_result"]["assistant_role"],
        "assistant_instructions": x["assistant_result"]["assistant_instructions"],
    })
)
