from typing import Dict

EMPTY_STR = ""


def is_empty(word: str):
    return bool(word == EMPTY_STR)


def is_empty_strip(word: str):
    return bool(word.strip() == EMPTY_STR)


def get_value(item: Dict, key: str):
    """
    If key not in item:
        - then return ""
    If key in item:
        - If None then return ""
        - If not None then return item[key]

    :param item:
    :param key:
    :return:
    """
    if key not in item:
        return ""
    if item[key] is None:
        return ""
    return item[key]


def log_id(request_id: str, message: str):
    """
    :param request_id: The request_id to use
    :param message: Real message
    :return:
    """
    return f"[{request_id}]{message}"
