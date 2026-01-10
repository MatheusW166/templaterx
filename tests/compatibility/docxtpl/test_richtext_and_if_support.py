from docxtpl import RichText
from src.templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx, template
from tests.helpers.faker import faker_pt_BR as faker
import pytest


@pytest.fixture
def docx_main(tmp_path: p.Path):
    return p.Paths(
        template=TEMPLATES_DIR / "richtext_and_if_tpl.docx",
        out=tmp_path / "out.docx",
    )


# -------------------------
# Tests
# -------------------------

def test_richtext_should_be_rendered_with_if_when_foobar_is_a_valid_richtext(docx_main):
    tplx = TemplaterX(docx_main.template)

    color = faker.hex_color()[1:]
    text = faker.paragraph()
    tplx.render({"foobar": RichText(text, color=color)})

    xml = docx.get_rendered_xml(tplx, docx_main.out)

    assert "COUCOU" in xml
    template.assert_text_has_property(
        xml, text,
        prop_tag="w:color",
        prop_attrs={"w:val": color}
    )


def test_if_block_should_be_processed_if_foobar_is_defined_but_is_falsy(docx_main):
    """
    When the variable used in an if block exists in the context but is falsy
    (including None), the if block should be processed normally, removing all 
    placeholders.
    """

    tplx = TemplaterX(docx_main.template)

    tplx.render({"foobar": None})
    xml = docx.get_rendered_xml(tplx, docx_main.out)

    assert not template.is_any_placeholder_present(xml)


def test_placeholders_should_be_kept_when_context_is_empty(docx_main):
    tplx = TemplaterX(docx_main.template)

    tplx.render({})

    xml = docx.get_rendered_xml(tplx, docx_main.out)

    assert r"{% if foobar %}" in xml
    assert r"{{ foobar }}" in xml
    assert r"COUCOU" in xml
    assert r"{% endif %}" in xml


def test_incremental_render_should_work_normally_with_richtext_and_if(docx_main):
    tplx = TemplaterX(docx_main.template)

    color = faker.hex_color()[1:]
    text = faker.paragraph()

    tplx.render({})
    tplx.render({"foobar": RichText(text, color=color)})

    xml = docx.get_rendered_xml(tplx, docx_main.out)

    assert "COUCOU" in xml
    template.assert_text_has_property(
        xml, text,
        prop_tag="w:color",
        prop_attrs={"w:val": color}
    )
