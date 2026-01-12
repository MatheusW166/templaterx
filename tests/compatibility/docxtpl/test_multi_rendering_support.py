from templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
import pytest


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "multi_rendering_tpl.docx",
        out=tmp_path / "out.docx",
    )


def test_multi_rendering_support(paths, tmp_path):
    tplx = TemplaterX(paths.template)

    documents = [
        {
            "dest_file": "multi_render1.docx",
            "context": {
                "title": "Title ONE",
                "body": "This is the body for first document",
            },
        },
        {
            "dest_file": "multi_render2.docx",
            "context": {
                "title": "Title TWO",
                "body": "This is the body for second document",
            },
        },
        {
            "dest_file": "multi_render3.docx",
            "context": {
                "title": "Title THREE",
                "body": "This is the body for third document",
            },
        },
    ]

    for data in documents:
        dest_file = tmp_path / data["dest_file"]
        context: dict = data["context"]
        tplx.render(context)
        tplx.save(dest_file)

        xml = docx.get_rendered_xml(tplx, dest_file)
        assert all(value in xml for value in context.values())
