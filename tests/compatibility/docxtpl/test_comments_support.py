import pytest
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx, template
from templaterx import TemplaterX


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "comments_tpl.docx",
        out=tmp_path / "out.docx",
    )


def test_comments_are_removed_from_rendered_doc(paths):
    tplx = TemplaterX(paths.template)
    tplx.render({})

    xml = docx.get_rendered_xml(tplx, paths.out)

    assert not template.is_any_comment_present(xml)
