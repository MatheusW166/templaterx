from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
from src.templaterx import TemplaterX
from docxtpl import R, Listing
import pytest


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "escape_tpl.docx",
        out=tmp_path / "out.docx",
    )


def test_escape_rich_text_listing_support(paths):
    tplx = TemplaterX(paths.template)

    context = {
        "myvar": R(
            '"less than" must be escaped : <, this can be done with RichText() or R()'
        ),
        "myescvar": 'It can be escaped with a "|e" jinja filter in the template too : < ',
        "mylisting": Listing("the listing\nwith\nsome\nlines\nand special chars : <>& ..."),
        "page_break": R("\f"),
        "new_listing": """
            This is a new listing
            Now, does not require Listing() Object
            Here is a \t tab\a
            Here is a new paragraph\a
            Here is a page break : \f
            That's it
        """,
        "some_html": (
            "HTTP/1.1 200 OK\n"
            "Server: Apache-Coyote/1.1\n"
            "Cache-Control: no-store\n"
            "Expires: Thu, 01 Jan 1970 00:00:00 GMT\n"
            "Pragma: no-cache\n"
            "Content-Type: text/html;charset=UTF-8\n"
            "Content-Language: zh-CN\n"
            "Date: Thu, 22 Oct 2020 10:59:40 GMT\n"
            "Content-Length: 9866\n"
            "\n"
            "<html>\n"
            "<head>\n"
            "    <title>Struts Problem Report</title>\n"
            "    <style>\n"
            "    \tpre {\n"
            "\t    \tmargin: 0;\n"
            "\t        padding: 0;\n"
            "\t    }    "
            "\n"
            "    </style>\n"
            "</head>\n"
            "<body>\n"
            "...\n"
            "</body>\n"
            "</html>"
        ),
    }

    tplx.render(context)
    tplx.render({
        "nlnp": R(
            "Here is a multiple\nlines\nstring\aand some\aother\aparagraphs",
            color="#ff00ff",
        ),
    })

    xml = docx.get_rendered_xml(tplx, paths.out)

    assert xml.count(r'w:val="ff00ff"') == 4
    assert "This is a new listing" in xml
    assert '"less than" must be escaped' in xml
