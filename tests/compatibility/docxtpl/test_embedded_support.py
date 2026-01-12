from templaterx import TemplaterX
from tests.helpers import hash as hs, paths as p, docx
from .constants import TEMPLATES_DIR
import pytest


EMBEDDED_EXCEL = "word/embeddings/Feuille_Microsoft_Office_Excel3.xlsx"
EMBEDDED_PPT = "word/embeddings/Pr_sentation_Microsoft_Office_PowerPoint4.pptx"


@pytest.fixture
def paths(tmp_path):
    templates = [
        "embedded_embedded_docx_tpl.docx",
        "embedded_main_tpl.docx",
        "embedded_dummy.docx",
        "embedded_static_docx.docx",
        "embedded_dummy2.docx",
        "real_Excel.xlsx",
        "real_PowerPoint.pptx",
    ]

    return {
        name: p.Paths(
            template=TEMPLATES_DIR / name,
            out=tmp_path / f"{name.replace('.', '_')}_out.docx",
        )
        for name in templates
    }


# -------------------------
# Helpers
# -------------------------

def render_docx(template, output, context):
    tplx = TemplaterX(template)
    tplx.render(context)
    tplx.save(output)
    return output


def build_dynamic_embedded_docx(paths):
    return render_docx(
        template=paths["embedded_embedded_docx_tpl.docx"].template,
        output=paths["embedded_embedded_docx_tpl.docx"].out,
        context={"name": "John Doe"},
    )


def build_main_document(paths, embedded_docx):
    tplx = TemplaterX(paths["embedded_main_tpl.docx"].template)

    tplx.replace_embedded(
        paths["embedded_dummy.docx"].template,
        paths["embedded_static_docx.docx"].template,
    )
    tplx.replace_embedded(
        paths["embedded_dummy2.docx"].template,
        embedded_docx,
    )

    tplx.replace_zipname(
        EMBEDDED_EXCEL,
        paths["real_Excel.xlsx"].template,
    )
    tplx.replace_zipname(
        EMBEDDED_PPT,
        paths["real_PowerPoint.pptx"].template,
    )

    tplx.render({"name": "John Doe"})
    tplx.save(paths["embedded_main_tpl.docx"].out)

    return paths["embedded_main_tpl.docx"].out


# -------------------------
# Tests
# -------------------------


def test_embedded_excel_and_powerpoint_are_replaced_correctly(paths):
    embedded = build_dynamic_embedded_docx(paths)
    output = build_main_document(paths, embedded)

    excel_bytes = docx.read_embedded_bytes(output, EMBEDDED_EXCEL)
    ppt_bytes = docx.read_embedded_bytes(output, EMBEDDED_PPT)

    assert hs.bytes_hash(excel_bytes) == hs.file_hash(
        paths["real_Excel.xlsx"].template
    )
    assert hs.bytes_hash(ppt_bytes) == hs.file_hash(
        paths["real_PowerPoint.pptx"].template
    )


def test_embedded_docx_files_are_present_and_correct(paths, tmp_path):
    embedded = build_dynamic_embedded_docx(paths)
    output = build_main_document(paths, embedded)

    embedded_hashes = {
        hs.file_hash(f)
        for f in docx.extract_all_embedded_docx_files(output, tmp_path)
    }

    assert hs.file_hash(
        paths["embedded_static_docx.docx"].template
    ) in embedded_hashes

    assert hs.file_hash(embedded) in embedded_hashes
