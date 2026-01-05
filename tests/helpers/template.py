import re


def is_any_placeholder_present(xml: str):
    return re.search(r"(\{\{.*?\}\})|(\{\%.*?\%\})", xml, re.DOTALL) is not None


def is_any_comment_present(xml: str):
    return re.search(r"\{\#.*?\#\}", xml, re.DOTALL) is not None


def xml_has_column(xml: str, column_name: str):
    return re.search(rf"<w:tc>.*?{column_name}.*?</w:tc>", xml) is not None
