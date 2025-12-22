import pytest
from faker import Faker
from src.templaterx import TemplaterX
from .helpers import docx, paths as p
from .constants import TEMPLATES_DIR


@pytest.fixture
def faker():
    return Faker()


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "simple_var.docx",
        out=tmp_path / "out.docx",
    )


def test_unique_var_is_rendered_correctly(faker, paths):
    tpl = TemplaterX(paths.template)

    value = faker.name()
    context = {"NAME": value}

    tpl.render(context)
    tpl.save(paths.out)

    text = docx.extract_text(paths.out)
    assert f"Hello, {value}!" in text


def test_unique_var_is_rendered_correctly_after_other_render_calls(faker, paths):

    tpl = TemplaterX(paths.template)

    value = faker.name()
    context = {"NAME": value}

    for _ in range(faker.random_number(1)):
        tpl.render({key: f"{key}_VALUE" for key in faker.words()})

    tpl.render(context)
    tpl.save(paths.out)

    text = docx.extract_text(paths.out)
    assert f"Hello, {value}!" in text


def test_unique_var_missing_does_not_break_render(paths):

    tpl = TemplaterX(paths.template)

    tpl.render({})
    tpl.save(paths.out)

    text = docx.extract_text(paths.out)

    assert r"Hello, {{ NAME }}" in text


def test_unique_var_is_rendered_only_when_defined(faker, paths):

    tpl = TemplaterX(paths.template)

    tpl.render({})

    value = faker.name()
    tpl.render({"NAME": value})

    tpl.save(paths.out)

    text = docx.extract_text(paths.out)
    assert f"Hello, {value}!" in text


def test_unique_var_first_render_wins(faker, paths):

    tpl = TemplaterX(paths.template)

    first = faker.name()
    second = faker.name()

    tpl.render({"NAME": first})
    tpl.render({"NAME": second})
    tpl.save(paths.out)

    text = docx.extract_text(paths.out)

    assert f"Hello, {first}!" in text
    assert second not in text


def test_unique_var_is_not_duplicated_after_multiple_renders(faker, paths):

    tpl = TemplaterX(paths.template)

    value = faker.name()

    for _ in range(faker.random_number(1)):
        tpl.render({"NAME": value})

    tpl.save(paths.out)

    text = docx.extract_text(paths.out)

    assert text.count(value) == 1


def test_unique_var_empty_value_is_rendered(paths):

    tpl = TemplaterX(paths.template)

    tpl.render({"NAME": ""})
    tpl.save(paths.out)

    text = docx.extract_text(paths.out)

    assert "Hello, !" in text


def test_unique_var_is_not_affected_by_irrelevant_context(faker, paths):

    tpl = TemplaterX(paths.template)

    irrelevant_context = {key: f"{key}_VALUE" for key in faker.words()}

    tpl.render(irrelevant_context)
    tpl.save(paths.out)

    text = docx.extract_text(paths.out)

    assert r"Hello, {{ NAME }}!" in text
