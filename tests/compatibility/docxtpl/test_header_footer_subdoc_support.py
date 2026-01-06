from src.templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
from tests.helpers.faker import faker_pt_BR as faker
import pytest


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "header_footer_tpl.docx",
        out=tmp_path / "out.docx",
    )


def test_header_footer_should_not_break_using_subdocs(paths):
    tplx = TemplaterX(paths.template)

    paragraph = faker.paragraph()

    sd = tplx.new_subdoc()
    sd.add_paragraph(paragraph)

    context = {
        "title": "Header and footer test",
        "company_name": faker.company(),
        "date": faker.date(),
        "mysubdoc": sd
    }

    tplx.render(context)
    xml = docx.get_rendered_xml(tplx, paths.out)

    assert paragraph in xml
    assert context["title"] in xml
    assert context["company_name"] in xml
    assert context["date"] in xml


def test_header_footer_should_not_break_using_subdocs_with_partial_render(paths):
    tplx = TemplaterX(paths.template)

    context_partial = {
        "title": "Header and footer test",
        "company_name": faker.company(),
        "date": faker.date()
    }

    tplx.render(context_partial)

    paragraph = faker.paragraph()
    sd = tplx.new_subdoc()
    sd.add_paragraph(paragraph)

    tplx.render({"mysubdoc": sd})
    xml = docx.get_rendered_xml(tplx, paths.out)

    assert paragraph in xml
    assert context_partial["title"] in xml
    assert context_partial["company_name"] in xml
    assert context_partial["date"] in xml
