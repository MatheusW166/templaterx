from src.templaterx import TemplaterX
from tests.helpers import paths as p, docx, faker, template
from .constants import TEMPLATES_DIR
import pytest
import re


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "dynamic_table_tpl.docx",
        out=tmp_path / "out.docx",
    )


def test_dynamic_tables_are_built_properly(paths):

    tplx = TemplaterX(paths.template)

    context: dict[str, list] = {
        "col_labels": faker.fake_word_list(),
        "tbl_contents": [
            {
                "label": faker.faker_pt_BR.word(),
                "cols": faker.fake_word_list(),
            },
            {
                "label": faker.faker_pt_BR.word(),
                "cols": faker.fake_word_list(),
            },
            {
                "label": faker.faker_pt_BR.word(),
                "cols": faker.fake_word_list(),
            },
        ],
    }

    tplx.render({})
    tplx.render(context)
    xml = docx.get_rendered_xml(tplx, paths.out)

    assert all([
        template.xml_has_column(xml, col_label)
        for col_label in context["col_labels"]
    ])

    assert all([
        template.xml_has_column(xml, label)
        for tbl_content in context["tbl_contents"]
        for label in tbl_content["label"]
    ])

    assert all([
        template.xml_has_column(xml, col_content)
        for tbl_content in context["tbl_contents"]
        for col_content in tbl_content["cols"]
    ])
