from typing import Any, Iterable
from docxtpl import RichText
import re

RichTextChunk = tuple[str | RichText, dict[str, Any]]


def rich_text_from_chunks(
    chunks: Iterable[RichTextChunk],
    *,
    base: RichText | None = None,
) -> RichText:
    rt = base or RichText()

    for content, options in chunks:
        rt.add(content, **options)

    return rt


def is_any_placeholder_present(xml: str):
    return re.search(r"(\{\{.*?\}\})|(\{\%.*?\%\})", xml, re.DOTALL) is not None


def is_any_comment_present(xml: str):
    return re.search(r"\{\#.*?\#\}", xml, re.DOTALL) is not None


def xml_has_column(xml: str, column_name: str):
    return re.search(rf"<w:tc>.*?{column_name}.*?</w:tc>", xml) is not None


def text_has_property(
    xml: str,
    text: str,
    *,
    prop_tag: str,
    prop_attrs: dict[str, str] | None = None,
):
    """
    Checks that a given text appears in a <w:r> run that
    contains the specified run property.

    Examples:
      - prop_tag="w:color", prop_attrs={"w:val": "ff00ff"}
      - prop_tag="w:strike", prop_attrs=None
      - prop_tag="w:shd", prop_attrs={"w:fill": "ffff00"}
    """

    attrs_pattern = ""
    if prop_attrs:
        attrs_pattern = "".join(
            rf'\s+{re.escape(k)}="{re.escape(v)}"'
            for k, v in prop_attrs.items()
        )

    pattern = re.compile(
        rf"""
        <w:r\b[^>]*>                  # run start
        .*?
        <w:rPr>.*?
        <{prop_tag}\b{attrs_pattern}\s*/?>
        .*?</w:rPr>
        .*?
        <w:t\b[^>]*>{re.escape(text)}.*?</w:t>
        .*?
        </w:r>
        """,
        re.DOTALL | re.VERBOSE,
    )

    return pattern.search(xml) is not None


def assert_text_has_property(
    xml: str,
    text: str,
    *,
    prop_tag: str,
    prop_attrs: dict[str, str] | None = None,
):
    has_prop = text_has_property(
        xml, text,
        prop_tag=prop_tag,
        prop_attrs=prop_attrs
    )
    assert has_prop, (
        f'Text "{text}" with run property '
        f'<{prop_tag} {prop_attrs or ""}> not found'
    )
