from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from typing import List
import time
import random
from urllib.parse import quote, quote_plus
from duckduckgo_search.exceptions import DuckDuckGoSearchException

# 创建 DuckDuckGoSearchAPIWrapper 单例实例，避免重复创建
_ddg_instance = None

# 记录上一次请求时间，用于实现限流
_last_request_time = 0
_min_request_interval = 2.0  # 两次请求之间的最小间隔（秒）


def get_ddg_instance():
    """获取 DuckDuckGoSearchAPIWrapper 的单例实例。"""
    global _ddg_instance

    if _ddg_instance is None:
        _ddg_instance = DuckDuckGoSearchAPIWrapper()

    return _ddg_instance


def web_search(web_query: str, num_results: int) -> List[str]:
    """
    执行网页搜索，并包含限流、重试以及降级搜索机制。
    参数：
        web_query：搜索请求
        num_results：返回结果数量
    返回：
        搜索结果 URL 列表
    """

    global _last_request_time

    # 执行请求限流
    current_time = time.time()

    time_since_last_request = (current_time - _last_request_time)

    if time_since_last_request < _min_request_interval:
        # 等待，避免触发请求限制
        sleep_time = (_min_request_interval - time_since_last_request + random.uniform(0.1, 0.5))
        print(f"触发搜索限流，等待 {sleep_time:.2f} 秒后继续请求...")
        time.sleep(sleep_time)

    # 使用 DuckDuckGo 搜索，并支持重试机制
    max_retries = 3
    base_delay = 2  # 基础重试等待时间（秒）

    for attempt in range(max_retries):
        try:
            # 更新最后一次请求时间
            _last_request_time = time.time()

            # 获取搜索结果
            ddg = get_ddg_instance()
            results = ddg.results(web_query, num_results)

            # 提取 URL
            urls = [r["link"] for r in results]

            # 如果获取成功则直接返回
            if urls:
                return urls
            else:
                print(f"搜索请求没有返回结果：{web_query}")

                # 如果没有结果，最后一次尝试后进入降级方案
                if attempt == max_retries - 1:
                    break
                time.sleep(1)  # 重试前短暂停顿

        except DuckDuckGoSearchException as e:
            if "Ratelimit" in str(e) and attempt < max_retries - 1:
                # 针对限流错误使用指数退避策略
                delay = (base_delay * (2 ** attempt) + random.uniform(0, 1))

                print(f"DuckDuckGo 触发限流，{delay:.2f} 秒后重试（第 {attempt + 1}/{max_retries} 次）")
                time.sleep(delay)
            else:
                print(f"DuckDuckGo 搜索失败：{str(e)}")
                break
        except Exception as e:
            print(f"网页搜索过程出错：{str(e)}")

            if attempt < max_retries - 1:
                # 其他异常使用普通重试机制
                delay = (base_delay + random.uniform(0, 1))
                print(f"{delay:.2f} 秒后重试（第 {attempt + 1}/{max_retries} 次）")
                time.sleep(delay)
            else:
                break

    # 如果执行到这里，说明搜索失败或没有结果
    # 启用降级搜索方案
    return fallback_search(web_query, num_results)


def fallback_search(query: str, num_results: int) -> List[str]:

    """
    DuckDuckGo 不可用或被限流时的降级搜索方案。
    返回可能相关的英文 Wikipedia 和通用英文资料来源链接。
    参数：
        query：搜索请求
        num_results：返回结果数量
    返回：
        可能相关的 URL 列表
    """

    print(f"使用降级搜索，搜索请求：{query}")

    # 清洗并预处理搜索请求
    query_clean = query.lower().strip()

    # 英文资料来源通常覆盖更广，后续由模型负责整理并翻译成中文
    general_sources = [
        "https://en.wikipedia.org/wiki/Main_Page",
        "https://www.britannica.com/",
        "https://www.worldcat.org/",
        "https://www.jstor.org/",
        "https://www.sciencedirect.com/",
        "https://www.researchgate.net/",
        "https://scholar.google.com/scholar?q=" + quote_plus(query_clean),
        "https://www.academia.edu/",
        "https://baike.baidu.com/",
        "https://www.zhihu.com/search?type=content&q=" + quote_plus(query_clean)
    ]

    # 根据搜索关键词生成英文 Wikipedia 链接
    wikipedia_urls = []

    # 提取潜在主题
    # 去除常见中英文疑问词与停用词
    stop_words = [
        "什么", "哪里", "何时", "为什么", "怎么", "如何", "是否", "可以", "应该", "以及",
        "关于", "介绍", "告诉", "我", "我们", "你", "的", "了", "在", "是", "和", "与",
        "或", "及", "对", "从", "到", "为", "把", "被", "这", "那", "一个", "一些",
        "what", "where", "when", "why", "how", "is", "are", "was", "were", "do", "does", "did",
        "can", "could", "would", "should", "might", "a", "an", "the", "in", "on", "at", "by", "for",
        "with", "about", "to", "of", "from", "as", "tell", "me", "you", "i", "we"
    ]

    # 中文通常没有空格；如果搜索词中有空格，则按词过滤，否则保留整句作为主题搜索。
    raw_words = query_clean.split()
    if len(raw_words) > 1:
        query_words = [word for word in raw_words if word not in stop_words]
    else:
        query_words = [query_clean] if query_clean and query_clean not in stop_words else []

    # 生成英文 Wikipedia 主题链接
    if len(query_words) >= 2:
        # 使用连续关键词组合生成主题
        for i in range(len(query_words) - 1):
            topic = "_".join([query_words[i], query_words[i + 1]])
            wikipedia_urls.append(f"https://en.wikipedia.org/wiki/{quote(topic)}")

    # 补充单关键词主题
    for word in query_words:
        if len(word) > 1:  # 仅保留有意义关键词
            wikipedia_urls.append(f"https://en.wikipedia.org/wiki/{quote(word)}")

    # 构造英文 Wikipedia 搜索链接
    search_query = quote_plus(query_clean)
    wikipedia_search_url = f"https://en.wikipedia.org/w/index.php?search={search_query}"
    wikipedia_urls.insert(0, wikipedia_search_url)

    # 合并通用来源与 Wikipedia 来源
    all_urls = wikipedia_urls + general_sources

    # 去重并保持顺序
    unique_urls = []
    for url in all_urls:
        if url not in unique_urls:
            unique_urls.append(url)

    # 返回前 N 个结果
    return unique_urls[:num_results]
