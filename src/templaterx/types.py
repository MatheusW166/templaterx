from os import PathLike
from typing import TYPE_CHECKING, Any, BinaryIO, Mapping, TypeAlias

if TYPE_CHECKING:
    from docx.document import Document
    from docx.opc.part import Part
else:
    Part = object
    Document = object

DocxPartType: TypeAlias = Part
DocumentType: TypeAlias = Document

Context: TypeAlias = Mapping[str, Any]
TemplateSource: TypeAlias = str | PathLike[str] | BinaryIO
