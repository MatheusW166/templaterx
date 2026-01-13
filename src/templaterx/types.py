from typing import TYPE_CHECKING, TypeAlias


if TYPE_CHECKING:
    from docx.opc.part import Part
    from docx.document import Document
else:
    Part = object
    Document = object

DocxPartType: TypeAlias = Part
DocumentType: TypeAlias = Document
