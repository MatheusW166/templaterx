from typing import TYPE_CHECKING, TypeAlias, Mapping, Any, BinaryIO
from os import PathLike


if TYPE_CHECKING:
    from docx.opc.part import Part
    from docx.document import Document
else:
    Part = object
    Document = object

DocxPartType: TypeAlias = Part
DocumentType: TypeAlias = Document

Context: TypeAlias = Mapping[str, Any]
TemplateSource: TypeAlias = str | PathLike[str] | BinaryIO
