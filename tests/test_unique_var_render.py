import pytest
from src.templaterx import TemplaterX
from .helpers import docx, paths as p
from .helpers.faker import faker_pt_BR as faker
from .constants import TEMPLATES_DIR


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "simple_var.docx",
        out=tmp_path / "out.docx",
    )


def test_var_is_rendered_when_defined(paths):
    tpl = TemplaterX(paths.template)

    value = faker.name()
    tpl.render({"NAME": value})

    text = docx.save_and_get_text(tpl, paths.out)

    assert f"Hello, {value}!" in text


def test_first_render_wins_and_value_is_not_duplicated(paths):
    tpl = TemplaterX(paths.template)

    first = faker.name()
    second = faker.name()

    tpl.render({"NAME": first})
    tpl.render({"NAME": second})
    tpl.render({"NAME": first})

    text = docx.save_and_get_text(tpl, paths.out)

    assert f"Hello, {first}!" in text
    assert second not in text
    assert text.count(first) == 1


def test_empty_value_is_rendered(paths):
    tpl = TemplaterX(paths.template)

    tpl.render({"NAME": ""})

    text = docx.save_and_get_text(tpl, paths.out)

    assert "Hello, !" in text


def test_placeholder_remains_when_var_is_missing(paths):
    tpl = TemplaterX(paths.template)

    tpl.render({})

    text = docx.save_and_get_text(tpl, paths.out)

    assert r"Hello, {{ NAME }}" in text


def test_irrelevant_context_does_not_affect_placeholder(paths):
    tpl = TemplaterX(paths.template)

    tpl.render({key: f"{key}_VALUE" for key in faker.words(3)})

    text = docx.save_and_get_text(tpl, paths.out)

    assert r"Hello, {{ NAME }}!" in text
