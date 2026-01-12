from docxtpl import InlineImage
from docx.shared import Mm
from templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
import pytest


@pytest.fixture
def docx_main(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "inline_image_tpl.docx",
        out=tmp_path / "out.docx",
    )


@pytest.fixture
def images():
    files = [
        "django.png",
        "python_logo.png",
        "python_jpeg.jpg",
        "zope.png",
        "pyramid.png",
        "bottle.png",
        "tornado.png"
    ]

    return {
        name: str(TEMPLATES_DIR / name)
        for name in files
    }


def test_inline_image_support(docx_main, images):
    tplx = TemplaterX(docx_main.template)

    context = {
        "myimage": InlineImage(tplx, images["python_logo.png"], width=Mm(20)),
        "myimageratio": InlineImage(
            tplx, images["python_jpeg.jpg"], width=Mm(30), height=Mm(60)
        ),
        "frameworks": [
            {
                "image": InlineImage(tplx, images["django.png"], height=Mm(10)),
                "desc": "The web framework for perfectionists with deadlines",
            },
            {
                "image": InlineImage(tplx, images["zope.png"], height=Mm(10)),
                "desc": "Zope is a leading Open Source Application Server "
                "and Content Management Framework",
            },
            {
                "image": InlineImage(tplx, images["pyramid.png"], height=Mm(10)),
                "desc": "Pyramid is a lightweight Python web framework aimed at taking "
                "small web apps into big web apps.",
            },
            {
                "image": InlineImage(tplx, images["bottle.png"], height=Mm(10)),
                "desc": "Bottle is a fast, simple and lightweight WSGI micro web-framework "
                "for Python",
            },
            {
                "image": InlineImage(tplx, images["tornado.png"], height=Mm(10)),
                "desc": "Tornado is a Python web framework and asynchronous networking "
                "library.",
            },
        ],
    }

    # Testing that it works also when autoescape has been forced to True
    tplx._jinja_env.autoescape = True

    tplx.render({})
    tplx.render(context)
    xml = docx.get_rendered_xml(tplx, docx_main.out)

    assert xml.count("python_logo.png") == 3
    assert all(img in xml for img in images.keys())
    assert all(row["desc"] in xml for row in context["frameworks"])
