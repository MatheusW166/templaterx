from templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
import pytest


@pytest.fixture
def docx_main(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "merge_docx_master_tpl.docx",
        out=tmp_path / "out.docx",
    )


@pytest.fixture
def docx_subdoc(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "merge_docx_subdoc.docx",
        out=tmp_path / "out.docx",
    )


def test_merge_subdoc_support(docx_main, docx_subdoc):
    tplx = TemplaterX(docx_main.template)

    sd = tplx.new_subdoc(docx_subdoc.template)
    tplx.render({})
    tplx.render({"mysubdoc": sd})

    xml = docx.get_rendered_xml(tplx, docx_main.out)

    assert all(
        img in xml for img in [
            "django.png",
            "python_logo.png",
            "python_jpeg.jpg",
            "zope.png",
            "pyramid.png",
            "bottle.png",
            "tornado.png"
        ]
    )
    assert all(desc in xml for desc in [
        "The web framework for perfectionists with deadlines",
        "Zope is a leading Open Source Application Server "
        "and Content Management Framework",
        "Pyramid is a lightweight Python web framework aimed at taking "
        "small web apps into big web apps.",
        "Bottle is a fast, simple and lightweight WSGI micro web-framework "
        "for Python",
        "Tornado is a Python web framework and asynchronous networking "
        "library."
    ])
