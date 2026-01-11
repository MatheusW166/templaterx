from src.templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx, template
import pytest


@pytest.fixture
def docx_main(tmp_path: p.Path):
    return p.Paths(
        template=TEMPLATES_DIR / "vertical_merge_nested_tpl.docx",
        out=tmp_path / "out.docx",
    )


def test_vertical_merge_nested_support(docx_main):

    tplx = TemplaterX(docx_main.template)
    tplx.render({})

    xml = docx.get_rendered_xml(tplx, docx_main.out)
    template.assert_vertical_merge(xml, cell_text="Group", total_rows=5)
