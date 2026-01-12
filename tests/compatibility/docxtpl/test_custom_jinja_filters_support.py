import pytest
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
from templaterx import TemplaterX
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
def fake_people_list():
    @dataclass
    class Person:
        name: str

    return [
        Person(name=faker.name())
        for _ in range(faker.random_int(min=2, max=100))
    ]


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


def test_complete_context_must_be_rendered_using_custom_filters(paths, jinja_env):

    tplx = TemplaterX(paths.template, jinja_env=jinja_env)

    doc_no = faker.random_int()
    context = {
        "base_value_string": {"saudation": "Hi,"},
        "doc_no": doc_no,
        "base_value_float": 1.5
    }

    tplx.render(context)
    xml = docx.get_rendered_xml(tplx, paths.out)

    assert f"The string value is Hi,"
    assert "Hi, Deric and John Doe" in xml
    assert f"Document Number : {doc_no}" in xml
    assert f"The float value is 1.5" in xml
    assert "3.5" in xml


def test_partial_context_must_render_available_data_even_using_custom_filters(paths, jinja_env):

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


def test_custom_filters_must_return_objects_properly(fake_people_list, paths, jinja_env):
    """
    This kind of syntax must work properly:

    {{ (people | first_row).name | trim }}
    """

    tplx = TemplaterX(paths.template, jinja_env=jinja_env)
    tplx.render({"people": fake_people_list})

    xml = docx.get_rendered_xml(tplx, paths.out)

    first_person = fake_people_list[0]
    assert f"First person: {first_person.name}" in xml


def test_custom_filters_must_keep_placeholders_of_objects_properly_when_context_is_undefined(fake_people_list, paths, jinja_env):
    tplx = TemplaterX(paths.template, jinja_env=jinja_env)
    tplx.render({})
    xml = docx.get_rendered_xml(tplx, paths.out)

    assert r"First person: {{ (people | first_row).name | trim }}" in xml


def test_edge_case_default_jinja_filter_must_replace_placeholders(fake_people_list, paths, jinja_env):
    """
    Default filter must keep its behavior.

    {{ (people | first_row).name | default(“default value”) }}
    """

    tplx = TemplaterX(paths.template, jinja_env=jinja_env)
    tplx.render({})
    tplx.render({"people": fake_people_list})
    xml = docx.get_rendered_xml(tplx, paths.out)

    default_result = r"First person default: default value"
    assert default_result in xml
