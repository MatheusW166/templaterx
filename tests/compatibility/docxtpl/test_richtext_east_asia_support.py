from src.templaterx import TemplaterX
from docxtpl import RichText
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx, template
import pytest


@pytest.fixture
def docx_main(tmp_path: p.Path):
    return p.Paths(
        template=TEMPLATES_DIR / "richtext_east_asia_tpl.docx",
        out=tmp_path / "out.docx",
    )


def test_richtext_east_asia_fonts_support(docx_main):
    tplx = TemplaterX(docx_main.template)

    rt = RichText("测试TEST", font="eastAsia:Microsoft YaHei")
    ch = RichText("测试TEST", font="eastAsia:微软雅黑")
    sun = RichText("测试TEST", font="eastAsia:SimSun")

    tplx.render({
        "example": rt,
        "Chinese": ch,
        "simsun": sun,
    })

    xml = docx.get_rendered_xml(tplx, docx_main.out)

    for font in (r"Microsoft YaHei", r"微软雅黑", r"SimSun"):
        template.assert_text_has_property(
            xml,
            r"测试TEST",
            prop_tag="w:rFonts",
            prop_attrs={
                "w:ascii": font,
                "w:hAnsi": font,
                "w:cs": font,
                "w:eastAsia": font,
            },
        )
