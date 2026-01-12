from typing import TYPE_CHECKING, TypeAlias


if TYPE_CHECKING:
    from docx.opc.part import Part
    from docxtpl.subdoc import Subdoc
    from docx.document import Document
else:
    Part = object
    Subdoc = object
    Document = object

DocxPartType: TypeAlias = Part
SubdocType: TypeAlias = Subdoc
DocumentType: TypeAlias = Document
