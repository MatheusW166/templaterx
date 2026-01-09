from typing import TYPE_CHECKING, TypeAlias


if TYPE_CHECKING:
    from docx.opc.part import Part
    from docx.shared import Mm
    from docxtpl.subdoc import Subdoc
else:
    Part = object
    Subdoc = object
    Mm = object

DocxPartType: TypeAlias = Part
SubdocType: TypeAlias = Subdoc
