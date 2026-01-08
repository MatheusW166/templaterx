from docxtpl import DocxTemplate
from ..types import DocxPartType


def get_footnotes(docx_tpl: DocxTemplate) -> DocxPartType | None:
    docx = docx_tpl.docx

    if not docx:
        return

    for section in docx.sections:
        if section.part.package is None:
            continue
        for part in section.part.package.parts:
            if part.content_type == (
                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.footnotes+xml"
            ):
                return part


def set_footnotes(docx_tpl: DocxTemplate, xml: str):
    footnotes_ref = get_footnotes(docx_tpl)
    if footnotes_ref:
        footnotes_ref._blob = xml.encode("utf-8")
