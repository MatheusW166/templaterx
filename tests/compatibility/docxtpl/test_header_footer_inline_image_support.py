from src.templaterx import TemplaterX
from src.types import Mm
from docxtpl import InlineImage
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
import pytest


@pytest.fixture
def paths(tmp_path):
    templates = [
        "header_footer_inline_image_tpl.docx",
        "django.png",
        "python.png",
    ]

    return {
        name: p.Paths(
            template=TEMPLATES_DIR / name,
            out=tmp_path / f"{name.replace('.', '_')}_out.docx",
        )
        for name in templates
    }


def test_header_footer_inline_image_support(paths):
    tplx = TemplaterX(paths["header_footer_inline_image_tpl.docx"].template)

    python_image = str(paths["python.png"].template)
    django_image = str(paths["django.png"].template)

    context = {
        "inline_image": InlineImage(tplx, django_image, height=Mm(10)),
        "images": [
            InlineImage(tplx, python_image, height=Mm(10)),
            InlineImage(tplx, python_image, height=Mm(10)),
            InlineImage(tplx, python_image, height=Mm(10)),
        ],
    }
    tplx.render({})
    tplx.render(context)

    output = paths["header_footer_inline_image_tpl.docx"].out
    xml = docx.get_rendered_xml(tplx, output)

    assert xml.count("django.png") == 1
    assert xml.count("python.png") == 3


def test_header_footer_inline_image_incremental_rendering_support(paths):
    tplx = TemplaterX(paths["header_footer_inline_image_tpl.docx"].template)

    python_image = str(paths["python.png"].template)
    django_image = str(paths["django.png"].template)

    context = {
        "images": [
            InlineImage(tplx, python_image, height=Mm(10)),
            InlineImage(tplx, python_image, height=Mm(10)),
            InlineImage(tplx, python_image, height=Mm(10)),
        ],
    }

    tplx.render(context)
    tplx.render({
        "inline_image": InlineImage(
            tplx,
            django_image,
            height=Mm(10)
        )
    })

    output = paths["header_footer_inline_image_tpl.docx"].out
    xml = docx.get_rendered_xml(tplx, output)

    assert xml.count("django.png") == 1
    assert xml.count("python.png") == 3


def test_header_footer_inline_image_undefined_vars_must_have_placeholders_preserved(paths):
    tplx = TemplaterX(paths["header_footer_inline_image_tpl.docx"].template)

    python_image = str(paths["python.png"].template)

    context = {
        "images": [
            InlineImage(tplx, python_image, height=Mm(10)),
            InlineImage(tplx, python_image, height=Mm(10)),
            InlineImage(tplx, python_image, height=Mm(10)),
        ],
    }

    tplx.render(context)

    output = paths["header_footer_inline_image_tpl.docx"].out
    xml = docx.get_rendered_xml(tplx, output)

    assert r"{{ inline_image }}" in xml
    assert "django.png" not in xml
    assert xml.count("python.png") == 3
