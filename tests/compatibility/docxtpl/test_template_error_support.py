from src.templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p
from jinja2.exceptions import TemplateError
import pytest


@pytest.fixture
def docx_main(tmp_path: p.Path):
    return p.Paths(
        template=TEMPLATES_DIR / "template_error_tpl.docx",
        out=tmp_path / "out.docx",
    )


def test_should_raise_template_error_when_pre_process_fails(docx_main):

    exc = None
    try:
        tplx = TemplaterX(docx_main.template)
        tplx.render({"test_variable": "test variable value"})
    except TemplateError as err:
        exc = err

    assert isinstance(exc, TemplateError)
