import pytest
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
from src.templaterx import TemplaterX
from jinja2 import Environment


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "custom_jinja_filters_tpl.docx",
        out=tmp_path / "out.docx",
    )


def test_custom_jinja_filters_must_work_properly(paths):

    def hello_name_filter(value_in_context, value_in_filter_arg):
        return value_in_context + " " + value_in_filter_arg

    def sum_values_filter(value_in_context, value_in_filter_arg):
        return value_in_context + value_in_filter_arg

    filters = {
        "hello_name_filter": hello_name_filter,
        "sum_values_filter": sum_values_filter
    }

    jinja_env = Environment()
    jinja_env.filters = filters

    tplx = TemplaterX(paths.template, jinja_env=jinja_env)

    # Should support incremental rendering with filters as well
    tplx.render({})
    tplx.render({})

    context = {"base_value_string": "Hello,", "base_value_float": 1.5}
    tplx.render(context)

    xml = docx.get_rendered_xml(tplx, paths.out)

    assert "Hello, Deric" in xml
    assert "3.5" in xml
