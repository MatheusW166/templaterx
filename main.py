from lxml import etree  # type: ignore
from dataclasses import dataclass
from os import PathLike
from typing import IO, Dict, Any, Optional, cast
from docxtpl import DocxTemplate
from jinja2 import Environment, meta
import re


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


class TemplaterX(DocxTemplate):
    def __init__(
        self,
        template_file: IO[bytes] | str | PathLike,
        jinja_env: Optional[Environment] = None
    ) -> None:
        self.jinja_env = jinja_env or Environment(
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.structures: Optional[list[Structure]] = None
        super().__init__(template_file)

    def render_init(self):
        # docxtpl
        self.init_docx()
        self.pic_map = {}
        self.current_rendering_part = None
        self.docx_ids_index = 1000
        self.is_saved = False

        # templaterx
        self.structures = None

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

    def _render_body_partial_context(self, context: dict[str, Any], jinja_env=None):
        if not self.docx:
            raise RuntimeError()

        if not self.structures:
            body_xml = self.get_xml()
            pre_processed_body_xml = self.patch_xml(body_xml)
            self.structures = self._extract_complete_structures(
                pre_processed_body_xml
            )

        structures_cp = self.structures[:]
        for idx, structure in enumerate(structures_cp):
            vars = self._extract_vars_from_template(structure.clob)
            if (vars - set(context.keys())):
                continue
            self.structures[idx].clob = self.render_xml_part(
                structure.clob,
                self.docx._part,
                context,
                jinja_env
            )
            self.structures[idx].is_rendered = True

        return self.structures

    def render_partial_context(
        self,
        context: Dict[str, Any]
    ):

        if not self.is_rendered or not self.docx:
            self.render_init()

        # Body
        structures = self._render_body_partial_context(context, self.jinja_env)

        parser = etree.XMLParser(recover=True)

        # Gets namespace.
        # It's gonna be within the first structure in most cases.
        nsmap_w: Optional[str] = None
        for s in structures:
            if nsmap_w is not None:
                break
            parsed = etree.fromstring(s.clob, parser=parser)
            if parsed is None:
                continue
            nsmap_w = cast(Optional[str], parsed.nsmap.get("w", nsmap_w))

        if not nsmap_w:
            raise ValueError("Attribute 'w' of Element.nsmap is 'None'")

        print(nsmap_w)

        exit(0)
        tree = "\n".join([
            etree.tostring(self.fix_tables(s.clob))
            if s.is_rendered
            else s.clob
            for s in structures
        ])

        tree = etree.fromstring(tree, parser=parser)
        self.fix_docpr_ids(tree)

        # Replace xml tree (body only)
        self.map_tree(tree)

        # # Headers
        # headers = self.build_headers_footers_xml(
        #     context, self.HEADER_URI, jinja_env)
        # for relKey, xml in headers:
        #     self.map_headers_footers_xml(relKey, xml)

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
tplx.save("_generated.docx")
