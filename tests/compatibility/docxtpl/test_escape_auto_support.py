from unicodedata import name
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
from src.templaterx import TemplaterX
import pytest


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "escape_tpl_auto.docx",
        out=tmp_path / "out.docx",
    )


def test_escape_auto_support(paths):
    # NOTE: All renders must be done before saving.

    XML_RESERVED = r"""<"&'>"""
    tplx = TemplaterX(paths.template, autoescape=True)

    tplx.render({})
    tplx.render({
        "nested_dict": {name(str(c)): c for c in XML_RESERVED},
        "autoescape_unicode": "This is an escaped <unicode> example \u4f60 & \u6211",
        "iteritems": lambda x: x.items(),
    })
    tplx.render({"autoescape": 'Escaped "str & ing"!'})

    xml = docx.get_rendered_xml(tplx, paths.out)

    assert 'Escaped "str &amp; ing"!' in xml
    assert "Less-than sign: &lt;" in xml
    assert 'Quotation mark: "' in xml
    assert "Ampersand: &amp;" in xml
    assert "Apostrophe: '" in xml
    assert "Greater-than sign: &gt;" in xml
    assert "This is an escaped &lt;unicode&gt; example 你 &amp; 我" in xml


def test_undefined_context_should_have_its_placeholders_preserved(paths):

    XML_RESERVED = r"""<"&'>"""
    tplx = TemplaterX(paths.template, autoescape=True)

    tplx.render({
        "nested_dict": {name(str(c)): c for c in XML_RESERVED},
        "autoescape_unicode": "This is an escaped <unicode> example \u4f60 & \u6211",
        "iteritems": lambda x: x.items(),
    })

    xml = docx.get_rendered_xml(tplx, paths.out)

    assert r"{{ autoescape }}" in xml
