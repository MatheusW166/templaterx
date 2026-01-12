from templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from .factories import RichTextTplDocxFactory
from tests.helpers import paths as p, docx
from tests.helpers.faker import faker_pt_BR as faker
import pytest


@pytest.fixture
def docx_main(tmp_path: p.Path):
    return p.Paths(
        template=TEMPLATES_DIR / "richtext_tpl.docx",
        out=tmp_path / "out.docx",
    )


def test_richtext_is_rendered_with_complete_context(docx_main: p.Paths):

    tplx = TemplaterX(docx_main.template)
    rt = RichTextTplDocxFactory.build_rich_text(tplx)

    random_paragraph = faker.paragraph()
    tplx.render({"example": rt, "INCREMENTAL_RENDER_VAR": random_paragraph})
    xml = docx.get_rendered_xml(tplx, docx_main.out)

    assert r"{{r context_variable }}" in xml
    assert random_paragraph in xml
    RichTextTplDocxFactory.assert_rich_text_is_rendered(xml)


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

    rt = RichTextTplDocxFactory.build_rich_text(tplx)
    tplx.render({"example": rt})

    xml = docx.get_rendered_xml(tplx, docx_main.out)

    assert r"{{r context_variable }}" in xml
    assert random_paragraph in xml
    RichTextTplDocxFactory.assert_rich_text_is_rendered(xml)
