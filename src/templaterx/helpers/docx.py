from templaterx.types import DocxPartType, DocumentType


def get_footnotes(docx: DocumentType) -> DocxPartType | None:
    for section in docx.sections:

        if section.part.package is None:
            continue

        for part in section.part.package.parts:
            if part.content_type == (
                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.footnotes+xml"
            ):
                return part


def set_footnotes(docx: DocumentType | None, xml: str) -> DocxPartType | None:
    if not docx:
        return

    footnotes_ref = get_footnotes(docx)
    if footnotes_ref:
        footnotes_ref._blob = xml.encode("utf-8")

    return footnotes_ref
