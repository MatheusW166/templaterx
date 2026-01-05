from unicodedata import name
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
from src.templaterx import TemplaterX
import pytest

XML_RESERVED = r"""<"&'>"""


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "escape_tpl_auto.docx",
        out=tmp_path / "out.docx",
    )


@pytest.fixture
def context():
    return {
        "nested_dict": get_nested_dict(),
        "autoescape_unicode": "This is an escaped <unicode> example \u4f60 & \u6211",
        "iteritems": iteritems,
    }


# -------------------------
# Helpers
# -------------------------


def get_nested_dict():
    return {name(str(c)): c for c in XML_RESERVED}


def iteritems(x: dict):
    return x.items()


# -------------------------
# Tests
# -------------------------


def test_escape_auto_support(paths, context):
    # NOTE: All renders must be done before saving.
    tplx = TemplaterX(paths.template, autoescape=True)

    tplx.render({})
    tplx.render(context)
    tplx.render({"autoescape": 'Escaped "str & ing"!'})

    xml = docx.get_rendered_xml(tplx, paths.out)

    assert 'Escaped "str &amp; ing"!' in xml
    assert "Less-than sign: &lt;" in xml
    assert 'Quotation mark: "' in xml
    assert "Ampersand: &amp;" in xml
    assert "Apostrophe: '" in xml
    assert "Greater-than sign: &gt;" in xml
    assert "This is an escaped &lt;unicode&gt; example 你 &amp; 我" in xml


def test_undefined_context_should_have_its_placeholders_preserved(paths, context):
    tplx = TemplaterX(paths.template, autoescape=True)

    tplx.render(context)

    xml = docx.get_rendered_xml(tplx, paths.out)

    assert r"{{ autoescape }}" in xml
