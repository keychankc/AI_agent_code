from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from utilities import to_obj

from llm_models import get_llm
from prompts import WEB_SEARCH_PROMPT_TEMPLATE

NUM_SEARCH_QUERIES = 3 # 生成多少个搜索词
NUM_SEARCH_RESULTS = 3 # 每个搜索词返回多少个网页
RESULT_TEXT_MAX_CHARACTERS = 20000 # 每个网页最多传入多少字符


# 搜索词生成链：把“用户问题 + 助手说明”转换成多个可直接用于搜索引擎的查询词
web_searches_chain = (
    RunnableLambda(lambda x:
        {
            'assistant_instructions': x['assistant_instructions'],
            'num_search_queries': NUM_SEARCH_QUERIES,
            'user_question': x['user_question']
        }
    )
    | WEB_SEARCH_PROMPT_TEMPLATE
    | get_llm() | StrOutputParser() | to_obj
)
