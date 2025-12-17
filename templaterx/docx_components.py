from dataclasses import dataclass, field
from typing import Literal, Optional
from docxtpl import DocxTemplate
from .helpers import docxtpl
from .structures import *

REL_ITEMS = Literal["headers", "footers"]
KEYS = Literal["body", "properties", "footnotes"] | REL_ITEMS


@dataclass
class DocxComponents():
    """
    Abstract representation of the main components of a DOCX file.
    """

    body: list[Structure] = field(default_factory=list)
    footnotes: list[Structure] = field(default_factory=list)
    properties: dict[str, list[Structure]] = field(default_factory=dict)
    headers: dict[str, list[Structure]] = field(default_factory=dict)
    footers: dict[str, list[Structure]] = field(default_factory=dict)

    def __getitem__(self, component: REL_ITEMS) -> dict[str, list[Structure]]:
        return getattr(self, component)

    def _get_structures(self, component: KEYS, relKey: Optional[str] = None) -> list[Structure]:
        structures = getattr(self, component)
        if isinstance(structures, dict):
            structures = structures.get(relKey, [])
        return structures

    def to_clob(self, component: KEYS, relKey: Optional[str] = None):
        structures = self._get_structures(component, relKey)
        return "".join([s.clob for s in structures])

    def is_component_rendered(self, component: KEYS, relKey: Optional[str] = None):
        structures = self._get_structures(component, relKey)
        return all([s.is_rendered for s in structures])


class DocxComponentsBuilder:
    """
    Builds a DocxComponents instance by extracting and pre-processing
    all XML parts of a DOCX template.

    This class is responsible ONLY for:
    - locating XML parts
    - patching XML
    - extracting Jinja2 structures

    It does NOT render any context.
    """

    def __init__(self, docx_template: DocxTemplate):
        self._docx_template = docx_template
        self._components = DocxComponents()

    @property
    def docx(self):
        docx = self._docx_template.docx
        if not docx:
            raise ValueError()
        return docx

    def build(self) -> DocxComponents:
        self._build_body()
        self._build_footnotes()
        # Properties -> Causes duplicated core error due to python-docx bug.
        # https://github.com/elapouya/python-docx-template/issues/558
        # self._build_properties()
        self._builder_headers_and_footers()
        return self._components

    def _pre_process_xml(self, xml: str) -> list[Structure]:
        patched_xml = self._docx_template.patch_xml(xml)
        return extract_jinja_structures_from_xml(patched_xml)

    def _build_body(self):
        xml = self._docx_template.get_xml()
        self._components.body = self._pre_process_xml(xml)

    def _build_footnotes(self):
        part = docxtpl.get_footnotes(self._docx_template)

        if not part:
            return

        xml = part.blob.decode("utf-8")
        self._components.footnotes = self._pre_process_xml(xml)

    def _build_properties(self):
        properties = [
            "author",
            "comments",
            "identifier",
            "language",
            "subject",
            "title",
        ]

        core = self.docx.core_properties

        for prop in properties:
            value = getattr(core, prop, None)
            if value:
                self._components.properties[prop] = self._pre_process_xml(
                    value
                )
            else:
                self._components.properties[prop] = []

    def _builder_headers_and_footers(self):
        self._build_relitem(self._docx_template.HEADER_URI)
        self._build_relitem(self._docx_template.FOOTER_URI)

    def _build_relitem(self, uri: str):
        component = "headers" if "/header" in uri else "footers"

        for relKey, part in self._docx_template.get_headers_footers(uri):

            structures = self._pre_process_xml(
                self._docx_template.get_part_xml(part)
            )

            self._components[component][relKey] = structures
