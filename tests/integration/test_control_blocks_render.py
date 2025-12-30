import pytest
from src.templaterx import TemplaterX, Context
from tests.helpers import docx, paths as p
from tests.helpers.faker import faker_pt_BR as faker
from tests.constants import TEMPLATES_DIR


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "control_blocks.docx",
        out=tmp_path / "out.docx",
    )


def test_p_for_block_is_kept_when_iterable_is_missing(paths):
    tpl = TemplaterX(paths.template)

    tpl.render({"VAR": faker.word(), "VAR1": faker.random_int()})
    xml = docx.get_rendered_xml(tpl, paths.out)

    assert r"{% for p in PARAGRAPH%}" in xml
    assert r"{{p}}" in xml
    assert r"{% endfor%}" in xml


def test_p_for_block_is_kept_when_inner_vars_are_missing(paths):
    tpl = TemplaterX(paths.template)

    tpl.render({"PARAGRAPH": [faker.name() for _ in range(3)]})
    xml = docx.get_rendered_xml(tpl, paths.out)

    assert r"{% for p in PARAGRAPH%}" in xml
    assert r"{{p}}" in xml
    assert r"{{VAR}}" in xml
    assert r"{{VAR1}}" in xml
    assert r"{% endfor%}" in xml


def test_p_for_block_is_rendered_when_all_vars_exist(paths):
    tpl = TemplaterX(paths.template)

    paragraph = [faker.name() for _ in range(3)]
    var = faker.word()
    var1 = faker.random_int()

    tpl.render({
        "PARAGRAPH": paragraph,
        "VAR": var,
        "VAR1": var1,
    })
    xml = docx.get_rendered_xml(tpl, paths.out)

    assert all(p in xml for p in paragraph)
    assert var in xml
    assert str(var1) in xml

    # Check if placeholders were removed
    assert r"{% for p in PARAGRAPH%}" not in xml
    assert r"{{p}}" not in xml


def test_table_for_block_is_kept_when_inner_vars_are_missing(paths):
    tpl = TemplaterX(paths.template)

    table = [faker.name() for _ in range(3)]

    tpl.render({"TABLE": table, "VAR1": 1, "VAR2": 1})
    xml = docx.get_rendered_xml(tpl, paths.out)

    assert r"{% for row in TABLE%}" in xml
    assert r"{{row}}" in xml
    assert r"{% if VAR1==1%}" in xml
    assert r"{% if VAR2==1%}" in xml
    assert r"{% if VAR3==1%}" in xml

    assert all(row not in xml for row in table)


def test_table_for_block_is_rendered_when_all_vars_exist(paths):
    tpl = TemplaterX(paths.template)

    table = [faker.name() for _ in range(3)]

    tpl.render({"TABLE": table, "VAR1": 1, "VAR2": 1, "VAR3": ""})
    xml = docx.get_rendered_xml(tpl, paths.out)

    assert all(row in xml for row in table)
    assert "COND1" in xml
    assert "COND2" not in xml

    # Check if placeholders were removed
    assert r"{% for row in TABLE%}" not in xml
    assert r"{{row}}" not in xml
    assert r"{% if VAR1==1%}" not in xml
    assert r"{% if VAR2==1%}" not in xml
    assert r"{% if VAR3==1%}" not in xml


def test_simple_variables_outside_blocks_follow_normal_rules(paths):
    tpl = TemplaterX(paths.template)

    value = faker.word()
    tpl.render({})
    tpl.render({"FREE": value})

    xml = docx.get_rendered_xml(tpl, paths.out)

    assert value in xml
    assert r"{{VAR}}" in xml
