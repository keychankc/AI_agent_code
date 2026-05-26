import requests
from bs4 import BeautifulSoup

def web_scrape(url: str) -> str:
    try:
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text(strip=True)

            return page_text
        else:
            return f"获取网页失败：状态码 {response.status_code}"
    except Exception as e:
        print(f"获取网页失败：{e}")
        return f"获取网页失败：{e}"
