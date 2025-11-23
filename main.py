import re
from jinja2 import Environment, meta
from docxtpl import DocxTemplate
from typing import IO, Dict, Any, cast
from os import PathLike
from dataclasses import dataclass, field
from typing import override
from typing import Literal


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
    clob: str
    is_rendered: bool = False

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
    headers: list[Structure] = field(default_factory=list)
    footers: list[Structure] = field(default_factory=list)
    properties: list[Structure] = field(default_factory=list)
    footnotes: list[Structure] = field(default_factory=list)

    Keys = Literal["body", "headers", "footers", "properties", "footnotes"]

    def to_clob(self, component: Keys):
        return "".join([s.clob for s in getattr(self, component)])

    def is_component_rendered(self, component: Keys):
        structures = getattr(self, component)
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
    def build_headers_footers_xml(self, context, uri, jinja_env=None):
        for relKey, part in self.get_headers_footers(uri):
            xml = self.get_part_xml(part)
            encoding = self.get_headers_footers_encoding(xml)
            xml = self.patch_xml(xml)
            if not self._is_all_vars_in_context(template=xml, context=context):
                continue
            xml = self.render_xml_part(xml, part, context, jinja_env)
            yield relKey, xml.encode(encoding)

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
        current_structure = Structure("")

        def match(pattern: str, text: str, group=0):
            m = re.match(pattern, text, flags=re.DOTALL)
            if m:
                try:
                    return cast(str, m.group(group))
                except:
                    pass
            return None

        def finish_current_structure():
            nonlocal current_structure
            structures.append(current_structure)
            current_structure = Structure("")

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
                finish_current_structure()

        return structures

    def _render_xml_part_partial_context(self, component_structures: list[Structure], xml: str, context: dict[str, Any]):
        if not self.docx:
            raise RuntimeError()

        if not component_structures:
            pre_processed_xml = self.patch_xml(xml)
            component_structures = self._extract_complete_structures(
                pre_processed_xml
            )

        for s in component_structures:
            if s.is_rendered or not self._is_all_vars_in_context(s.clob, context):
                continue
            s.clob = self.render_xml_part(
                s.clob,
                self.docx._part,  # type: ignore
                context,
                self._jinja_env
            )
            s.is_rendered = True

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

        tree = self.fix_tables(self._docx_components.to_clob("body"))

        self.fix_docpr_ids(tree)

        # Replace xml tree (body only)
        self.map_tree(tree)

        # with open("rendered.xml", "w") as f:
        #     f.write(etree.tostring(self.docx._element, encoding="unicode"))

        # Headers
        headers = self.build_headers_footers_xml(
            context, self.HEADER_URI, self._jinja_env)

        for relKey, xml in headers:
            self.map_headers_footers_xml(relKey, xml)

        # # Footers
        # footers = self.build_headers_footers_xml(
        #     context, self.FOOTER_URI, jinja_env)
        # for relKey, xml in footers:
        #     self.map_headers_footers_xml(relKey, xml)

        # self.render_properties(context, jinja_env)

        # self.render_footnotes(context, jinja_env)

        # set rendered flag

        self.is_rendered = True


context = {
    "LISTA": ["A", "B", "C"],
    "VARIAVEL": "Apenas uma variável",
    "VARIAVEL2": "'COLOQUEI NO FOOTNOTE'",
    "VAR_NAO_DEFINIDA": 2,
}

tplx = TemplaterX("template.docx")
tplx.render_partial_context(context)
tplx.save("_generated2.docx")
