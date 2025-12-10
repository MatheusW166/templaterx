import re
from jinja2 import Environment, meta
from docxtpl import DocxTemplate
from typing import IO, Dict, Any, cast, Optional, override, Literal
from os import PathLike
from dataclasses import dataclass, field


def index_vars_in_structures(structures: list[str]):

    def extract_vars_from_template(template: str):
        parsed = Environment().parse(template)
        return set(meta.find_undeclared_variables(parsed))

    vars_per_structure: list[set[str]] = [set() for _ in structures]
    cooccurrence_map: dict[str, set[str]] = {}

    for structure_index, template in enumerate(structures):
        extracted_vars = extract_vars_from_template(template)

        if not extracted_vars:
            continue

        vars_per_structure[structure_index] |= extracted_vars

        for var in extracted_vars:
            existing = cooccurrence_map.get(var, set())
            cooccurrence_map[var] = existing | (extracted_vars - {var})

    return vars_per_structure, cooccurrence_map


def collect_connected_vars(start_var: str, cooccurrence_map: dict[str, set[str]]):
    stack = [start_var]
    visited: set[str] = set()
    result: set[str] = set()

    while stack:
        var = stack.pop()

        if var in visited:
            continue

        visited.add(var)
        result.add(var)

        for neighbor in cooccurrence_map.get(var, ()):
            if neighbor not in visited:
                stack.append(neighbor)
            result.add(neighbor)

    return result


@dataclass
class Structure():
    clob = ""
    is_control_block = False
    is_rendered = False

    def __add__(self, other: str):
        if isinstance(other, str):
            self.clob += other
            return self
        raise TypeError("Unsupported operand type for +")

    def __radd__(self, other: str):
        return self.__add__(other)

    def __str__(self) -> str:
        return self.clob


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

    Keys = Literal["body", "headers", "footers", "properties", "footnotes"]

    def _get_structures(self, component: Keys, relKey: Optional[str] = None):
        structures = getattr(self, component)
        if isinstance(structures, dict):
            structures = structures.get(relKey, [])
        return structures

    def to_clob(self, component: Keys, relKey: Optional[str] = None):
        structures = self._get_structures(component, relKey)
        return "".join([s.clob for s in structures])

    def is_component_rendered(self, component: Keys, relKey: Optional[str] = None):
        structures = self._get_structures(component, relKey)
        return all([s.is_rendered for s in structures])


class TemplaterX(DocxTemplate):
    def __init__(
        self,
        template_file: IO[bytes] | str | PathLike,
        jinja_env=Environment(trim_blocks=True, lstrip_blocks=True)
    ) -> None:
        self._jinja_env = jinja_env
        self._docx_components = DocxComponents()
        super().__init__(template_file)

    @override
    def render_init(self):
        super().render_init()
        self._docx_components = DocxComponents()

    @override
    def save(self, filename: IO[bytes] | str | PathLike, *args, **kwargs) -> None:
        # Replacing original document

        # Body
        if self._docx_components.is_component_rendered("body"):
            tree = self.fix_tables(self._docx_components.to_clob("body"))
            self.fix_docpr_ids(tree)
            self.map_tree(tree)

        # Headers
        for relKey in self._docx_components.headers.keys():
            if self._docx_components.is_component_rendered("headers", relKey):
                xml = self._docx_components.to_clob("headers", relKey)
                self.map_headers_footers_xml(relKey, xml)

        # Footers
        for relKey in self._docx_components.footers.keys():
            if self._docx_components.is_component_rendered("footers", relKey):
                xml = self._docx_components.to_clob("footers", relKey)
                self.map_headers_footers_xml(relKey, xml)

        # Properties
        for prop in self._docx_components.properties.keys():
            if self._docx_components.is_component_rendered("properties", prop):
                xml = self._docx_components.to_clob("properties", prop)
                setattr(self.docx.core_properties, prop, xml)  # type: ignore

        # Footnotes
        footnotes = self._docx_components.to_clob("footnotes").encode("utf-8")
        self._get_footnotes()._blob = footnotes  # type: ignore

        return super().save(filename, *args, **kwargs)

    def _get_footnotes(self):
        if not self.docx:
            raise ValueError("'docx' is not defined")

        for section in self.docx.sections:
            if section.part.package is None:
                continue
            for part in section.part.package.parts:
                if part.content_type == (
                    "application/vnd.openxmlformats-officedocument"
                    ".wordprocessingml.footnotes+xml"
                ):
                    return part

    def _render_footnotes_partial_context(self, context: Dict[str, Any]) -> list[Structure]:
        footnotes = self._get_footnotes()

        if not footnotes:
            return []

        xml = footnotes.blob.decode("utf-8")
        return self._render_xml_part_partial_context(
            self._docx_components.footnotes,
            xml,
            context
        )

    def _render_properties_partial_context(self, context):
        # List of string attributes of docx.opc.coreprops.CoreProperties which are strings.
        # It seems that some attributes cannot be written as strings. Those are commented out.
        properties = [
            "author",
            # 'category',
            "comments",
            # 'content_status',
            "identifier",
            # 'keywords',
            "language",
            # 'last_modified_by',
            "subject",
            "title",
            # 'version',
        ]

        if not self.docx:
            raise ValueError("'docx' is not defined")

        for prop in properties:
            xml = getattr(self.docx.core_properties, prop)
            structures = self._docx_components.properties.get(prop, [])
            structures = self._render_xml_part_partial_context(
                structures,
                xml,
                context
            )
            yield prop, structures

    def _render_relitem_partial_context(self, uri: str, context):
        for relKey, part in self.get_headers_footers(uri):
            xml = self.get_part_xml(part)
            encoding = self.get_headers_footers_encoding(xml)

            structures = self._docx_components.headers.get(relKey, [])
            structures = self._render_xml_part_partial_context(
                structures,
                xml,
                context
            )

            for s in structures:
                if s.is_rendered:
                    s.clob = s.clob.encode(encoding).decode(encoding)

            yield relKey, structures

    def _is_all_vars_in_context(self, template: str, context: dict[str, Any]):
        vars_from_template = self._extract_vars_from_template(template)
        return len(vars_from_template - set(context.keys())) == 0

    def _extract_vars_from_template(self, template: str):
        parsed = Environment().parse(template)
        return set(meta.find_undeclared_variables(parsed))

    def _extract_complete_structures(self, xml: str):
        control_block_pattern = r"(\{\%.*?\%\})"
        tokens: list[str] = re.split(
            control_block_pattern,
            xml,
            flags=re.DOTALL
        )

        # Anything like {%...%} without "end"
        open_pattern = r"\{\%\s*(?!.*end).*?\%\}"

        # Anything like {% end... %}
        close_pattern = r"\{\%\s*end.*?\%\}"

        # Gets the reserved word, example:
        # {% for... %} => for, {% if... %} => if
        reserved_word_pattern = r"\{\%\s*(\S+)"

        close_block_expected_stack: list[str] = []
        structures: list[Structure] = []
        current_structure = Structure()

        def match(pattern: str, text: str, group=0):
            m = re.match(pattern, text, flags=re.DOTALL)
            if m:
                try:
                    return cast(str, m.group(group))
                except:
                    pass
            return None

        def finish_current_structure(is_control_block=False):
            nonlocal current_structure
            current_structure.is_control_block = is_control_block
            structures.append(current_structure)
            current_structure = Structure()

        for token in tokens:
            current_structure += token

            open_block = match(open_pattern, token)
            if open_block:
                reserved_word = match(reserved_word_pattern, open_block, 1)

                if not reserved_word:
                    raise RuntimeError(open_block)

                close_block_expected = "end"+reserved_word
                close_block_expected_stack.append(close_block_expected)
                continue

            close_block = match(close_pattern, token)
            if not close_block and not close_block_expected_stack:
                finish_current_structure()
                continue

            if not close_block:
                continue

            if not close_block_expected_stack:
                raise RuntimeError(f"No open block found\n{current_structure}")

            if close_block_expected_stack[-1] in close_block:
                close_block_expected_stack.pop()

            if not close_block_expected_stack:
                finish_current_structure(is_control_block=True)

        return structures

    def _render_xml_part_partial_context(self, component_structures: list[Structure], xml: str, context: dict[str, Any]):

        if not component_structures:
            pre_processed_xml = self.patch_xml(xml)
            component_structures = self._extract_complete_structures(
                pre_processed_xml
            )

        def render(structure: Structure):
            structure.clob = self.render_xml_part(
                structure.clob,
                None,
                context,
                self._jinja_env
            )
            structure.is_rendered = True

        for structure in component_structures:
            if not structure.is_control_block:
                render(structure)
            elif not structure.is_rendered and self._is_all_vars_in_context(structure.clob, context):
                render(structure)

        return component_structures

    def render_partial_context(
        self,
        context: Dict[str, Any]
    ):

        if not self.is_rendered or not self.docx:
            self.render_init()

        # Body
        self._docx_components.body = self._render_xml_part_partial_context(
            component_structures=self._docx_components.body,
            xml=self.get_xml(),
            context=context
        )

        # Headers
        for relKey, structures in self._render_relitem_partial_context(self.HEADER_URI, context):
            self._docx_components.headers[relKey] = structures

        # Footers
        for relKey, structures in self._render_relitem_partial_context(self.FOOTER_URI, context):
            self._docx_components.footers[relKey] = structures

        # Properties
        for prop, structures in self._render_properties_partial_context(context):
            self._docx_components.properties[prop] = structures

        # Footnotes
        self._docx_components.footnotes = self._render_footnotes_partial_context(
            context
        )

        self.is_rendered = True


context = {
    "LISTA": ["A", "B", "C"],
    "VARIAVEL": "Apenas uma variável",
    "VARIAVEL2": "'COLOQUEI NO FOOTNOTE'",
    "VAR_NAO_DEFINIDA": 2,
}

tplx = TemplaterX("template.docx")
tplx.render_partial_context(context)
# tplx.render_partial_context({"CABECALHO": "ESTE É O CABECALHO"})
tplx.save("_generated2.docx")
