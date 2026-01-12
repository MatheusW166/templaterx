from templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from .factories import RichtextParagraphTplDocxFactory
from tests.helpers import paths as p, docx
import pytest


@pytest.fixture
def docx_main(tmp_path: p.Path):
    return p.Paths(
        template=TEMPLATES_DIR / "richtext_paragraph_tpl.docx",
        out=tmp_path / "out.docx",
    )


def test_richtext_paragraph_should_render_with_complete_context(docx_main):
    tplx = TemplaterX(docx_main.template)

    rtp = RichtextParagraphTplDocxFactory.build_richtext_paragraph()
    tplx.render({"example": rtp})

    xml = docx.get_rendered_xml(tplx, docx_main.out)
    RichtextParagraphTplDocxFactory.assert_richtext_paragraph_is_rendered(xml)


def test_placeholder_should_be_kept_when_context_is_empty(docx_main):
    tplx = TemplaterX(docx_main.template)

    tplx.render({})

    xml = docx.get_rendered_xml(tplx, docx_main.out)
    assert r"{{ example }}" in xml


def test_richtext_paragraph_should_support_incremental_render(docx_main):
    tplx = TemplaterX(docx_main.template)

    tplx.render({})
    tplx.render({"xpto": 1})

    rtp = RichtextParagraphTplDocxFactory.build_richtext_paragraph()
    tplx.render({"example": rtp})

    xml = docx.get_rendered_xml(tplx, docx_main.out)
    RichtextParagraphTplDocxFactory.assert_richtext_paragraph_is_rendered(xml)
