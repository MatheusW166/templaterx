import pytest
from src.templaterx import TemplaterX
from .helpers import docx,  paths as p
from .helpers.faker import faker_pt_BR as faker
from .constants import TEMPLATES_DIR


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "multiple_vars.docx",
        out=tmp_path / "out.docx",
    )


def test_all_vars_are_rendered_when_defined(paths):
    tpl = TemplaterX(paths.template)

    context = {
        "NAME": faker.name(),
        "CITY": faker.city(),
        "JOB": faker.job(),
    }

    tpl.render(context)

    text = docx.save_and_get_text(tpl, paths.out)

    for value in context.values():
        assert value in text


def test_each_var_first_render_wins(paths):
    tpl = TemplaterX(paths.template)

    first_name = faker.name()
    second_name = faker.name()
    first_city = faker.city()

    tpl.render({"NAME": first_name, "CITY": first_city})
    tpl.render({"NAME": second_name})

    text = docx.save_and_get_text(tpl, paths.out)

    assert first_name in text
    assert first_city in text
    assert second_name not in text


def test_empty_values_are_rendered(paths):
    tpl = TemplaterX(paths.template)

    context = {
        "NAME": "",
        "CITY": "",
        "JOB": "",
    }

    tpl.render(context)

    text = docx.save_and_get_text(tpl, paths.out)

    assert "Name:" in text
    assert "City:" in text
    assert "Job:" in text
    assert r"{{ NAME }}" not in text
    assert r"{{ CITY }}" not in text
    assert r"{{ JOB }}" not in text


def test_placeholders_remains_when_vars_are_missing(paths):
    tpl = TemplaterX(paths.template)

    tpl.render({})

    text = docx.save_and_get_text(tpl, paths.out)

    assert r"{{ NAME }}" in text
    assert r"{{ CITY }}" in text
    assert r"{{ JOB }}" in text


def test_partial_context_is_supported(paths):
    tpl = TemplaterX(paths.template)

    name = faker.name()
    city = faker.city()

    tpl.render({"NAME": name, "CITY": city})

    text = docx.save_and_get_text(tpl, paths.out)

    assert name in text
    assert city in text
    assert r"{{ JOB }}" in text


def test_multiple_renders_do_not_duplicate_values(paths):
    tpl = TemplaterX(paths.template)

    context = {
        "NAME": faker.name(),
        "CITY": faker.city(),
    }

    tpl.render(context)
    tpl.render(context)
    tpl.render(context)

    text = docx.save_and_get_text(tpl, paths.out)

    for value in context.values():
        assert text.count(value) == 1
