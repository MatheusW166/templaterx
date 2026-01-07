from src.templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
import pytest


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "merge_paragraph_tpl.docx",
        out=tmp_path / "out.docx",
    )


def test_merge_paragraph_support(paths):
    tplx = TemplaterX(paths.template)
    tplx.render({"living_in_town": True})

    xml = docx.get_rendered_xml(tplx, paths.out)

    assert "My house is located\xa0</w:t>" in xml
    assert "in urban area\xa0</w:t>" in xml
    assert "and I love it.</w:t>" in xml
