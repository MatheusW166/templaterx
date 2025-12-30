from dataclasses import dataclass, field
from typing import Literal, Optional, TypeAlias
from docxtpl import DocxTemplate
from .helpers import docxtpl
from .structures import *

RelItems: TypeAlias = Literal["headers", "footers"]
CoreItems: TypeAlias = Literal["body", "footnotes"]
ComponentKey: TypeAlias = CoreItems | RelItems


@dataclass
class DocxComponents():
    """
    Abstract representation of the main components of a DOCX file.
    """

    body: list[Structure] = field(default_factory=list)
    footnotes: list[Structure] = field(default_factory=list)
    headers: dict[str, list[Structure]] = field(default_factory=dict)
    footers: dict[str, list[Structure]] = field(default_factory=dict)

    _blocks_adjacency: dict[str, set[str]] = field(default_factory=dict)
    _template_vars: set[str] = field(default_factory=set)

    def __getitem__(self, component: RelItems) -> dict[str, list[Structure]]:
        return getattr(self, component)

    def _get_structures(self, component: ComponentKey, relKey: Optional[str] = None) -> list[Structure]:
        structures = getattr(self, component)
        if not isinstance(structures, dict):
            return structures
        if relKey is None:
            return [item for v in structures.values() for item in v]
        return structures[relKey]

    def to_clob(self, component: ComponentKey, relKey: Optional[str] = None):
        structures = self._get_structures(component, relKey)
        return "".join([s.clob for s in structures])

    def is_component_rendered(self, component: ComponentKey, relKey: Optional[str] = None):
        structures = self._get_structures(component, relKey)
        return all([s.is_rendered for s in structures])

    def get_connected_vars(self, var: str) -> set[str]:
        return collect_control_blocks_connected_vars(var, self._blocks_adjacency)

    def get_all_vars(self) -> set[str]:
        return {*self._template_vars}


class DocxComponentsBuilder:
    """
    Builds a DocxComponents instance by extracting and pre-processing
    all XML parts of a DOCX template.

    This class is responsible for:
    - locating XML parts
    - patching XML
    - extracting Jinja2 structures
    - creating the adjacency list of control blocks
    - creating a list of all template variables
    """

    def __init__(self, docx_template: DocxTemplate):
        self._components = DocxComponents()
        self._docx_template = docx_template
        self._blocks_adjacency: dict[str, set[str]] = {}
        self._template_vars: set[str] = set()

    @property
    def docx(self):
        docx = self._docx_template.docx
        if not docx:
            raise ValueError()
        return docx

    def build(self) -> DocxComponents:
        self._build_body()
        self._build_footnotes()
        self._builder_headers_and_footers()
        self._components._template_vars = self._template_vars
        self._components._blocks_adjacency = self._blocks_adjacency
        return self._components

    def _add_in_adjacency_map(self, structures: list[Structure]):
        map = self._blocks_adjacency
        control_blocks_var_adjacency_map(structures, map)

    def _add_in_template_vars(self, structures: list[Structure]):
        for vars in extract_vars_from_structures(structures):
            self._template_vars |= vars

    def _pre_process_xml(self, xml: str) -> list[Structure]:
        patched_xml = self._docx_template.patch_xml(xml)
        structures = extract_jinja_structures_from_xml(patched_xml)
        self._add_in_adjacency_map(structures)
        self._add_in_template_vars(structures)
        return structures

    def _build_body(self):
        xml = self._docx_template.get_xml()
        self._components.body = self._pre_process_xml(xml)

    def _build_footnotes(self):
        part = docxtpl.get_footnotes(self._docx_template)

        if not part:
            return

        xml = part.blob.decode("utf-8")
        self._components.footnotes = self._pre_process_xml(xml)

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
