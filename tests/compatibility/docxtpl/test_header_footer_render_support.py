from templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
from tests.helpers.faker import faker_pt_BR as faker
import pytest


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "header_footer_entities_tpl.docx",
        out=tmp_path / "out.docx",
    )


def test_header_footer_should_render_properly(paths):
    tplx = TemplaterX(paths.template)

    context = {
        "title": faker.paragraph(),
    }

    tplx.render(context)
    xml = docx.get_rendered_xml(tplx, paths.out)

    assert context["title"] in xml
