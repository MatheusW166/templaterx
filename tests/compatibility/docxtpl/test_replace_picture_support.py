from templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx, hash as hs
from pathlib import Path
from random import randint
import pytest


@pytest.fixture
def docx_main(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "replace_picture_tpl.docx",
        out=tmp_path / "out.docx",
    )


@pytest.fixture
def target_image_path():

    images = [
        "python_jpeg.jpg",
        "bottle.png",
        "django.png",
        "dummy_pic_for_header.png",
        "pyramid.png",
        "python.png",
        "tornado.png",
        "zope.png"
    ]

    return TEMPLATES_DIR / images[randint(0, len(images)-1)]


def test_replace_picture_support(docx_main: p.Paths, target_image_path: Path, tmp_path):

    tplx = TemplaterX(docx_main.template)

    tplx.replace_pic(pic_in_docx_name="python_logo.png", dst=target_image_path)
    tplx.render({})
    tplx.save(docx_main.out)

    images_in_rendered_docx_paths = docx.extract_all_images(
        docx_main.out, tmp_path
    )
    assert len(images_in_rendered_docx_paths) == 1

    old_image_path = docx.extract_all_images(docx_main.template, tmp_path)[0]
    image_after_replace_path = images_in_rendered_docx_paths[0]

    assert hs.file_hash(old_image_path) != hs.file_hash(
        image_after_replace_path
    )
    assert hs.file_hash(
        image_after_replace_path
    ) == hs.file_hash(target_image_path)
