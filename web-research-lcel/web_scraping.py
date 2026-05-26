import requests
from bs4 import BeautifulSoup

def web_scrape(url: str) -> str:
    """抓取网页正文文本。"""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        if response.status_code != 200:
            return f"无法获取网页内容，状态码：{response.status_code}"

        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    except Exception as e:
        return f"无法获取网页内容：{e}"