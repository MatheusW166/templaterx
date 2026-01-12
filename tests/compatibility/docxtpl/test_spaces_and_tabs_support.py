from docxtpl import RichText
from templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
import pytest
import re


@pytest.fixture
def docx_main(tmp_path: p.Path):
    return p.Paths(
        template=TEMPLATES_DIR / "spaces_and_tabs_tpl.docx",
        out=tmp_path / "out.docx",
    )


# -------------------------
# Helpers
# -------------------------

def has_n_tabs(xml: str, *, text: str, nb_tabs: int):
    result = re.search(
        rf"""
        <w:p\b[^>]*>
            (?:
                (?!</w:p>).
            )*?
            {re.escape(text)}
            (?:
                (?!</w:p>).
            )*?
        </w:p>
        """,
        xml, re.DOTALL | re.VERBOSE
    )
    return result and result.group().count(r"<w:tab/>") == nb_tabs


def has_n_spaces(xml: str, *, text: str, nb_spaces: int):
    result = re.search(
        rf"""
        <w:r>\s*
            <w:t\s+xml:space="preserve">
                \x20{{{nb_spaces}}}
            </w:t>\s*
        </w:r>\s*
        <w:r>\s*
            <w:t\s+xml:space="preserve">
                \s+{re.escape(text)}
            </w:t>\s*
        </w:r>
        """,
        xml, re.DOTALL | re.VERBOSE
    )
    return result is not None


# -------------------------
# Tests
# -------------------------

def test_spaces_and_tabs_should_be_rendered(docx_main):
    tplx = TemplaterX(docx_main.template)

    tplx.render({
        "test_space": 10 * " ",
        "test_tabs": 5 * "\t",
        "test_space_r": RichText(10 * " "),
        "test_tabs_r": RichText(5 * "\t"),
    })

    xml = docx.get_rendered_xml(tplx, docx_main.out)

    assert f"{" "*12} Test spaces in template" in xml
    assert f"{" "*10} Test spaces with normal variable" in xml
    assert has_n_spaces(xml, text="Test spaces with richtext", nb_spaces=10)

    assert f"{"\t"*5} Test tabs in template"
    assert has_n_tabs(xml, text="Test tabs with normal variable", nb_tabs=5)
    assert has_n_tabs(xml, text="Test tabs with richtext", nb_tabs=5)


def test_spaces_and_tabs_should_work_normally_with_incremental_render(docx_main):
    tplx = TemplaterX(docx_main.template)

    tplx.render({"test_space": 10 * " "})
    tplx.render({"test_tabs": 5 * "\t"})
    tplx.render({"test_space_r": RichText(10 * " ")})
    tplx.render({"test_tabs_r": RichText(5 * "\t")})

    xml = docx.get_rendered_xml(tplx, docx_main.out)

    assert f"{" "*12} Test spaces in template" in xml
    assert f"{" "*10} Test spaces with normal variable" in xml
    assert has_n_spaces(xml, text="Test spaces with richtext", nb_spaces=10)

    assert f"{"\t"*5} Test tabs in template"
    assert has_n_tabs(xml, text="Test tabs with normal variable", nb_tabs=5)
    assert has_n_tabs(xml, text="Test tabs with richtext", nb_tabs=5)


def test_placeholders_should_be_kept(docx_main):
    tplx = TemplaterX(docx_main.template)

    tplx.render({})

    xml = docx.get_rendered_xml(tplx, docx_main.out)

    assert r"{{ test_space }}" in xml
    assert r"{{ test_tabs }}" in xml
    assert r"{{ test_space_r }}" in xml
    assert r"{{ test_tabs_r }}" in xml

    # Vars defined directly in the template should render normally
    assert f"{" "*12} Test spaces in template" in xml
    assert f"{"\t"*5} Test tabs in template"
