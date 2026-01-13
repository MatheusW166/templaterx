from typing import Protocol, Iterable
from .types import DocumentType, DocxPartType


class TplPreProcessorProtocol(Protocol):

    docx: DocumentType | None

    HEADER_URI = (
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/header"
    )
    FOOTER_URI = (
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer"
    )

    def patch_xml(self, src_xml: str) -> str: ...

    def get_xml(self) -> str: ...

    def get_headers_footers(
        self,
        uri: str
    ) -> Iterable[tuple[str, DocxPartType],]: ...

    def get_part_xml(self, part: DocxPartType) -> str: ...
