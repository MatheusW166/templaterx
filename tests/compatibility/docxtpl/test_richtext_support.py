import re
from docxtpl import RichText
from src.templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
from tests.helpers.faker import faker_pt_BR as faker
import pytest


@pytest.fixture
def docx_main(tmp_path: p.Path):
    return p.Paths(
        template=TEMPLATES_DIR / "richtext_tpl.docx",
        out=tmp_path / "out.docx",
    )


# -------------------------
# Helpers
# -------------------------

def build_rich_text(tplx: TemplaterX):
    rt = RichText()
    rt.add("a rich text", style="myrichtextstyle")
    rt.add(" with ")
    rt.add("some italic", italic=True)
    rt.add(" and ")
    rt.add("some violet", color="#ff00ff")
    rt.add(" and ")
    rt.add("some striked", strike=True)
    rt.add(" and ")
    rt.add("some Highlighted", highlight="#ffff00")
    rt.add(" and ")
    rt.add("some small", size=14)
    rt.add(" or ")
    rt.add("big", size=60)
    rt.add(" text.")
    rt.add("\nYou can add an hyperlink, here to ")
    rt.add("google", url_id=tplx.build_url_id("http://google.com"))
    rt.add("\nEt voilà ! ")
    rt.add("\n1st line")
    rt.add("\n2nd line")
    rt.add("\n3rd line")
    rt.add("\aA new paragraph : <cool>\a")
    rt.add("--- A page break here (see next page) ---\f")

    for ul in [
        "single",
        "double",
        "thick",
        "dotted",
        "dash",
        "dotDash",
        "dotDotDash",
        "wave",
    ]:
        rt.add("\nUnderline : " + ul + " \n", underline=ul)  # type: ignore

    rt.add("\nFonts :\n", underline=True)
    rt.add("Arial\n", font="Arial")
    rt.add("Courier New\n", font="Courier New")
    rt.add("Times New Roman\n", font="Times New Roman")
    rt.add("\n\nHere some")
    rt.add("superscript", superscript=True)
    rt.add(" and some")
    rt.add("subscript", subscript=True)

    rt_embedded = RichText("an example of ")
    rt_embedded.add(rt)

    return rt_embedded


def assert_text_has_property(
    xml: str,
    text: str,
    *,
    prop_tag: str,
    prop_attrs: dict[str, str] | None = None,
):
    """
    Asserts that a given text appears in a <w:r> run that
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

    assert pattern.search(xml), (
        f'Text "{text}" with run property '
        f'<{prop_tag} {prop_attrs or ""}> not found'
    )


def assert_contains_lines(xml: str, lines: list[str]):
    for line in lines:
        assert f">{line}<" in xml


def assert_rich_props(xml: str, cases: list[tuple]):
    for text, tag, attrs in cases:
        assert_text_has_property(
            xml,
            text,
            prop_tag=tag,
            prop_attrs=attrs,
        )


def assert_rich_text_is_rendered(xml: str):
    RICH_PROPERTIES = [
        ("a rich text", "w:rStyle", {"w:val": "myrichtextstyle"}),
        ("some italic", "w:i", None),
        ("some violet", "w:color", {"w:val": "ff00ff"}),
        ("some striked", "w:strike", None),
        ("some Highlighted", "w:shd", {"w:fill": "ffff00"}),
        ("some small", "w:sz", {"w:val": "14"}),
        ("big", "w:sz", {"w:val": "60"}),
        ("superscript", "w:vertAlign", {"w:val": "superscript"}),
        ("subscript", "w:vertAlign", {"w:val": "subscript"}),
    ]

    UNDERLINES = [
        "single",
        "double",
        "thick",
        "dotted",
        "dash",
        "dotDash",
        "dotDotDash",
        "wave",
    ]

    FONTS = [
        "Arial",
        "Courier New",
        "Times New Roman",
    ]

    assert re.search(
        r'<w:hyperlink\b[^>]*>.*?<w:t[^>]*>google</w:t>',
        xml, re.DOTALL
    )

    assert_contains_lines(
        xml,
        [
            "You can add an hyperlink, here to ",
            "Et voilà ! ",
            "1st line",
            "2nd line",
            "3rd line",
        ],
    )

    assert r"A new paragraph : &lt;cool&gt;" in xml
    assert '<w:br w:type="page"/>' in xml

    assert_rich_props(xml, RICH_PROPERTIES)

    for ul in UNDERLINES:
        assert_text_has_property(
            xml,
            f"Underline : {ul}",
            prop_tag="w:u",
            prop_attrs={"w:val": ul},
        )

    for font in FONTS:
        assert_text_has_property(
            xml,
            font,
            prop_tag="w:rFonts",
            prop_attrs={
                "w:ascii": font,
                "w:hAnsi": font,
                "w:cs": font,
            },
        )


# -------------------------
# Tests
# -------------------------


def test_richtext_is_rendered_with_complete_context(docx_main: p.Paths):

    tplx = TemplaterX(docx_main.template)
    rt = build_rich_text(tplx)

    random_paragraph = faker.paragraph()
    tplx.render({"example": rt, "INCREMENTAL_RENDER_VAR": random_paragraph})
    xml = docx.get_rendered_xml(tplx, docx_main.out)

    assert r"{{r context_variable }}" in xml
    assert random_paragraph in xml
    assert_rich_text_is_rendered(xml)


def test_all_placeholders_are_kept_with_empty_context(docx_main: p.Paths):

    tplx = TemplaterX(docx_main.template)

    tplx.render({})
    xml = docx.get_rendered_xml(tplx, docx_main.out)

    assert r"{{r context_variable }}" in xml
    assert r"{{ example }}" in xml
    assert r"{{ INCREMENTAL_RENDER_VAR }}" in xml


def test_rich_text_should_support_incremental_render(docx_main: p.Paths):

    tplx = TemplaterX(docx_main.template)

    tplx.render({})

    random_paragraph = faker.paragraph()
    tplx.render({"INCREMENTAL_RENDER_VAR": random_paragraph})

    rt = build_rich_text(tplx)
    tplx.render({"example": rt})

    xml = docx.get_rendered_xml(tplx, docx_main.out)

    assert r"{{r context_variable }}" in xml
    assert random_paragraph in xml
    assert_rich_text_is_rendered(xml)
