import pytest
from src.templaterx import TemplaterX
from .helpers import docx, template, paths as p
from .helpers.faker import faker_pt_BR as faker
from .constants import TEMPLATES_DIR


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "simple_var.docx",
        out=tmp_path / "out.docx",
    )


def test_vars_are_rendered_in_all_docx_components(paths):
    tpl = TemplaterX(paths.template)

    body = faker.name()
    header = faker.name()
    footer = faker.name()
    footnotes = faker.name()

    tpl.render({
        "BODY_NAME": body,
        "HEADER_NAME": header,
        "FOOTER_NAME": footer,
        "FOOTNOTE_NAME": footnotes,
    })

    text = docx.get_rendered_xml(tpl, paths.out)

    assert f"BODY_{body}" in text
    assert f"HEADER_{header}" in text
    assert f"FOOTER_{footer}" in text
    assert f"FOOTNOTE_{footnotes}" in text


def test_partial_render_is_suported(paths):
    tpl = TemplaterX(paths.template)

    body = faker.name()
    footnotes = faker.name()

    tpl.render({
        "BODY_NAME": body,
        "FOOTNOTE_NAME": footnotes,
    })

    text = docx.get_rendered_xml(tpl, paths.out)

    assert f"BODY_{body}" in text
    assert r"HEADER_{{ HEADER_NAME }}" in text
    assert r"FOOTER_{{ FOOTER_NAME }}" in text
    assert f"FOOTNOTE_{footnotes}" in text


def test_first_render_wins_for_all_components(paths):
    tpl = TemplaterX(paths.template)

    first = {
        "BODY_NAME": faker.name(),
        "HEADER_NAME": faker.name(),
        "FOOTER_NAME": faker.name(),
        "FOOTNOTE_NAME": faker.name(),
    }

    second = {
        "BODY_NAME": faker.name(),
        "HEADER_NAME": faker.name(),
        "FOOTER_NAME": faker.name(),
        "FOOTNOTE_NAME": faker.name(),
    }

    tpl.render(first)
    tpl.render(second)

    text = docx.get_rendered_xml(tpl, paths.out)

    assert f"BODY_{first["BODY_NAME"]}" in text
    assert f"HEADER_{first["HEADER_NAME"]}" in text
    assert f"FOOTER_{first["FOOTER_NAME"]}" in text
    assert f"FOOTNOTE_{first["FOOTNOTE_NAME"]}" in text

    for value in second.values():
        assert value not in text


def test_empty_values_are_rendered_in_all_components(paths):
    tpl = TemplaterX(paths.template)

    tpl.render({
        "BODY_NAME": "",
        "HEADER_NAME": "",
        "FOOTER_NAME": "",
        "FOOTNOTE_NAME": "",
    })

    xml = docx.get_rendered_xml(tpl, paths.out)

    assert not template.is_any_placeholder_present(xml)


def test_placeholders_remain_when_vars_are_missing(paths):
    tpl = TemplaterX(paths.template)

    tpl.render({})

    text = docx.get_rendered_xml(tpl, paths.out)

    assert r"BODY_{{ BODY_NAME }}" in text
    assert r"HEADER_{{ HEADER_NAME }}" in text
    assert r"FOOTER_{{ FOOTER_NAME }}" in text
    assert r"FOOTNOTE_{{ FOOTNOTE_NAME }}" in text


def test_irrelevant_context_does_not_affect_any_component(paths):
    tpl = TemplaterX(paths.template)

    tpl.render({key: f"{key}_VALUE" for key in faker.words(5)})

    text = docx.get_rendered_xml(tpl, paths.out)

    assert r"BODY_{{ BODY_NAME }}" in text
    assert r"HEADER_{{ HEADER_NAME }}" in text
    assert r"FOOTER_{{ FOOTER_NAME }}" in text
    assert r"FOOTNOTE_{{ FOOTNOTE_NAME }}" in text
