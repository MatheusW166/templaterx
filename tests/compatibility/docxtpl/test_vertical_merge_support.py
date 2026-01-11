from src.templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx, template
import pytest


@pytest.fixture
def docx_main(tmp_path: p.Path):
    return p.Paths(
        template=TEMPLATES_DIR / "vertical_merge_tpl.docx",
        out=tmp_path / "out.docx",
    )


def test_book_cell_should_work_with_incremental_render(docx_main):

    tplx = TemplaterX(docx_main.template)
    tplx.render({})

    tplx.render({
        "total_price": "10,000.00",
    })

    context = {
        "items": [
            {"desc": "Python interpreters", "qty": 2, "price": "FREE"},
            {"desc": "Django projects", "qty": 5403, "price": "FREE"},
            {"desc": "Guido", "qty": 1, "price": "100,000,000.00"},
        ],
        "category": "Book",
    }
    tplx.render(context)

    xml = docx.get_rendered_xml(tplx, docx_main.out)

    template.assert_vertical_merge(
        xml, cell_text="Book",
        total_rows=len(context["items"])
    )
    assert r"10,000.00" in xml
