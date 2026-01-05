import pytest
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
from src.templaterx import TemplaterX
from docxtpl import RichText


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "cellbg_tpl.docx",
        out=tmp_path / "out.docx",
    )


def test_cells_and_texts_are_filled_with_its_defined_colors(paths):
    tplx = TemplaterX(paths.template)

    context = {
        "alerts": [
            {
                "date": "2015-03-10",
                "desc": RichText("Very critical alert", color="FF0000", bold=True),
                "type": "CRITICAL",
                "bg": "FF0000",
            },
            {
                "date": "2015-03-11",
                "desc": RichText("Just a warning"),
                "type": "WARNING",
                "bg": "FFDD00",
            },
            {
                "date": "2015-03-12",
                "desc": RichText("Information"),
                "type": "INFO",
                "bg": "8888FF",
            },
            {
                "date": "2015-03-13",
                "desc": RichText("Debug trace"),
                "type": "DEBUG",
                "bg": "FF00FF",
            },
        ],
    }

    tplx.render({})
    tplx.render(context)

    xml = docx.get_rendered_xml(tplx, paths.out)

    assert 'val="FF0000"' in xml
    assert 'fill="FF0000"' in xml
    assert 'fill="FFDD00"' in xml
    assert 'fill="8888FF"' in xml
    assert 'fill="FF00FF"' in xml
    assert xml.count("w:fill") == 4
