import re


def is_any_placeholder_present(xml: str):
    return re.search(r"(\{\{.*?\}\})|(\{\%.*?\%\})", xml, re.DOTALL) is not None


def is_any_comment_present(xml: str):
    return re.search(r"\{\#.*?\#\}", xml, re.DOTALL) is not None
