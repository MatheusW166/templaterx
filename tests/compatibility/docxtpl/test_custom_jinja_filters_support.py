import pytest
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
from src.templaterx import TemplaterX
from jinja2 import Environment
from tests.helpers.faker import faker_pt_BR as faker
from dataclasses import dataclass


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "custom_jinja_filters_tpl.docx",
        out=tmp_path / "out.docx",
    )


@pytest.fixture
def jinja_env():
    def hello_name_filter(value_in_context, value_in_filter_arg):
        return value_in_context + " " + value_in_filter_arg

    def sum_values_filter(value_in_context, value_in_filter_arg):
        return value_in_context + value_in_filter_arg

    def first_row(data: list):
        return data[0]

    custom_filters = {
        "hello_name_filter": hello_name_filter,
        "sum_values_filter": sum_values_filter,
        "first_row": first_row
    }

    env = Environment()

    native_filters = env.filters
    env.filters = {**native_filters,  **custom_filters}

    return env


def test_custom_jinja_filters_must_work_properly_with_custom_and_native_filters(paths, jinja_env):

    tplx = TemplaterX(paths.template, jinja_env=jinja_env)

    context = {
        "base_value_string": {"saudation": "Hi,"},
        "base_value_float": 1.5
    }

    tplx.render(context)

    xml = docx.get_rendered_xml(tplx, paths.out)

    assert f"The float value is {context["base_value_float"]}"
    assert f"The string value is {context["base_value_string"]}"
    assert "Hi, Deric and John Doe" in xml
    assert "3.5" in xml


def test_incremental_rendering_must_work_with_filters(paths, jinja_env):

    tplx = TemplaterX(paths.template, jinja_env=jinja_env)

    doc_no = faker.random_int()
    context = {
        "base_value_string": {"saudation": "Hi,"},
        "doc_no": doc_no
    }

    tplx.render({})
    tplx.render(context)

    xml = docx.get_rendered_xml(tplx, paths.out)

    # Defined context must be rendered
    assert f"The string value is Hi,"
    assert "Hi, Deric and John Doe" in xml
    assert f"Document Number : {doc_no}" in xml

    # Undefined context must have its placeholders preserved
    assert r"The float value is {{ base_value_float }}" in xml
    assert r"The filter modified float value is {{ base_value_float | sum_values_filter(2) }}" in xml

    # This render should fill the remaining float data
    tplx.render({"base_value_float": 1.5})
    xml = docx.get_rendered_xml(tplx, paths.out)

    assert f"The float value is 1.5" in xml
    assert "3.5" in xml


def test_custom_filters_must_return_objects_properly(paths, jinja_env):
    """
    This kind of syntax must work properly:

    {{ (people | first_row).name | trim }}
    """

    @dataclass
    class Person:
        name: str

    people = [
        Person(name=faker.name())
        for _ in range(faker.random_int(min=2, max=100))
    ]

    tplx = TemplaterX(paths.template, jinja_env=jinja_env)
    tplx.render({})
    xml = docx.get_rendered_xml(tplx, paths.out)

    # Undefined context must have its placeholders preserved
    assert r"First person: {{ (people | first_row).name | trim }}" in xml

    # We must be able to render the context later
    tplx.render({"people": people})
    xml = docx.get_rendered_xml(tplx, paths.out)

    first_person = people[0]
    assert f"First person: {first_person.name}" in xml
