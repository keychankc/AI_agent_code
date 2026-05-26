import json


def to_obj(text: str):
    """将 JSON 字符串转换为 Python 对象。"""
    return json.loads(text)
