from jinja2 import Environment
from dataclasses import dataclass, field
from typing import Literal, TypeAlias, cast, overload
from .helpers import docx, structures as st
from .structure import Structure
from .types import DocxPartType
from .protocols import TplPreProcessorProtocol

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

    _parts: dict[ComponentKey, DocxPartType | dict[str, DocxPartType]] = field(
        default_factory=dict
    )

    def __getitem__(self, component: RelItems) -> dict[str, list[Structure]]:
        return getattr(self, component)

    def _get_structures(self, component: ComponentKey, relKey: str | None = None) -> list[Structure]:
        structures = getattr(self, component)
        if not isinstance(structures, dict):
            return structures
        if relKey is None:
            return [item for v in structures.values() for item in v]
        return structures[relKey]

    @overload
    def set_part(self, part: DocxPartType, component: CoreItems) -> None: ...

    @overload
    def set_part(
        self,
        part: DocxPartType,
        component: RelItems,
        relKey: str
    ) -> None: ...

    def set_part(self, part: DocxPartType, component: CoreItems | RelItems, relKey: str | None = None):
        if relKey is None:
            self._parts[component] = part
            return
        self._parts[component] = self._parts.get(component, dict())
        cast(dict, self._parts[component])[relKey] = part

    @overload
    def get_part(self, component: CoreItems) -> DocxPartType | None: ...

    @overload
    def get_part(
        self,
        component: RelItems,
        relKey: str
    ) -> DocxPartType | None: ...

    def get_part(self, component: CoreItems | RelItems, relKey: str | None = None) -> DocxPartType | None:
        part = self._parts.get(component)
        if not part:
            return None
        if not isinstance(part, dict):
            return part
        if not relKey:
            raise ValueError("'relKey' cannot be None")
        return part[relKey]

    def to_clob(self, component: ComponentKey, relKey: str | None = None):
        return "".join([s.clob for s in self._get_structures(component, relKey)])

    def is_component_rendered(self, component: ComponentKey, relKey: str | None = None):
        return all([s.is_rendered for s in self._get_structures(component, relKey)])

    def get_connected_vars(self, var: str) -> set[str]:
        return st.collect_control_blocks_connected_vars(var, self._blocks_adjacency)

    def get_all_vars(self) -> set[str]:
        return {*self._template_vars}


class DocxComponentsBuilder:
    """
    Builds a DocxComponents instance by extracting and pre-processing
    all XML parts of a DOCX template.
    """

    def __init__(self, tpp: TplPreProcessorProtocol, jinja_env: Environment | None = None, skip_pre_process=False):
        self._jinja_env = jinja_env
        self._skip_pre_process = skip_pre_process
        self._components = DocxComponents()
        self._blocks_adjacency: dict[str, set[str]] = {}
        self._template_vars: set[str] = set()
        self._tpp = tpp

    @property
    def _docx(self):
        docx = self._tpp.docx
        if not docx:
            raise ValueError("'docx' is not defined")
        return docx

    def build(self) -> DocxComponents:
        self._build_body()
        self._build_footnotes()
        self._builder_headers_and_footers()
        self._components._template_vars = self._template_vars
        self._components._blocks_adjacency = self._blocks_adjacency
        return self._components

    def _add_in_adjacency_map(self, structures: list[Structure]):
        adj_map = self._blocks_adjacency
        st.control_blocks_var_adjacency_map(structures, prev=adj_map)

    def _add_in_template_vars(self, structures: list[Structure]):
        for vars in st.extract_vars_from_structures(structures, self._jinja_env):
            self._template_vars |= vars

    def _pre_process_xml(self, xml: str) -> list[Structure]:

        if self._skip_pre_process:
            return st.extract_jinja_structures_from_xml(xml)

        patched_xml = self._tpp.patch_xml(xml)
        structures = st.extract_jinja_structures_from_xml(patched_xml)
        self._add_in_adjacency_map(structures)
        self._add_in_template_vars(structures)
        return structures

    def _build_body(self):
        xml = self._tpp.get_xml()
        self._components.body = self._pre_process_xml(xml)
        self._components.set_part(self._docx._part, "body")

    def _build_footnotes(self):
        part = docx.get_footnotes(self._docx)

        if not part:
            return

        xml = part.blob.decode("utf-8")
        self._components.footnotes = self._pre_process_xml(xml)
        self._components.set_part(part, "footnotes")

    def _builder_headers_and_footers(self):
        self._build_relitem(self._tpp.HEADER_URI)
        self._build_relitem(self._tpp.FOOTER_URI)

    def _build_relitem(self, uri: str):
        component = "headers" if "/header" in uri else "footers"

        for relKey, part in self._tpp.get_headers_footers(uri):
            structures = self._pre_process_xml(
                self._tpp.get_part_xml(part)
            )
            self._components[component][relKey] = structures
            self._components.set_part(part, component, relKey)
