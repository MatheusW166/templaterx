from templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
from tests.helpers.faker import faker_pt_BR as faker
import pytest


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "header_footer_tpl_utf8.docx",
        out=tmp_path / "out.docx",
    )


def test_header_footer_utf8_support(paths):
    tplx = TemplaterX(paths.template)

    sd = tplx.new_subdoc()

    paragraph = faker.paragraph()
    sd.add_paragraph(paragraph)

    context = {
        "title": "헤더와 푸터",
        "company_name": "세계적 회사",
        "date": faker.date(),
    }

    tplx.render(context)
    tplx.render({"mysubdoc": sd})

    xml = docx.get_rendered_xml(tplx, paths.out)

    assert all(value in xml for value in context.values())
    assert paragraph in xml
