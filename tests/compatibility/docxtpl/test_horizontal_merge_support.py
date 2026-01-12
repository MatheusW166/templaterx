from templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
import pytest


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "horizontal_merge_tpl.docx",
        out=tmp_path / "out.docx",
    )


def test_horizontal_merge_support(paths):
    tplx = TemplaterX(paths.template)
    tplx.render({})

    xml = docx.get_rendered_xml(
        tplx, paths.out
    ).split("Actual output.")[-1]

    assert all(xml.count(f"Item {i+1}") == 1 for i in range(3))
    assert all(xml.count(f"Header {i+1}") == 1 for i in range(3))
    assert all(xml.count(f"Subheader {i+1}") == 1 for i in range(4))
    assert xml.count("Footer") == 1
