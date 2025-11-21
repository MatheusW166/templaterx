from typing import Dict, Any, Optional
from docxtpl import DocxTemplate
import random
from jinja2 import Environment, meta
from typing import cast
import re


def match(pattern: str, text: str, group=0):
    m = re.match(pattern, text, flags=re.DOTALL)

    if m:
        try:
            return cast(str, m.group(group))
        except:
            pass

    return None


def extract_complete_structures(xml: str):
    control_block_pattern = r"(\{\%.*?\%\})"
    tokens: list[str] = re.split(control_block_pattern, xml, flags=re.DOTALL)

    # Anything like {%...%} without "end"
    open_pattern = r"\{\%\s*(?!.*end).*?\%\}"

    # Anything like {% end... %}
    close_pattern = r"\{\%\s*end.*?\%\}"

    # Gets the reserved word, example:
    # {% for... %} => for, {% if... %} => if
    reserved_word_pattern = r"\{\%\s*(\S+)"

    close_block_expected_stack: list[str] = []
    structures: list[str] = []
    current_structure = ""

    def finish_current_structure():
        nonlocal current_structure
        structures.append(current_structure.strip())
        current_structure = ""

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
            raise RuntimeError("No open block found\n"+current_structure)

        if close_block_expected_stack[-1] in close_block:
            close_block_expected_stack.pop()

        if not close_block_expected_stack:
            finish_current_structure()

    return structures


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


with open("pre-processed.xml", "r") as f:
    clob = f.read()

structures = extract_complete_structures(clob)
vars_per_structure, cooccurrence_map = index_vars_in_structures(structures)
vars = collect_connected_vars("LISTA2", cooccurrence_map)


env = Environment(trim_blocks=True, lstrip_blocks=True)


context = {
    "LISTA": ["A", "B", "C"],
    "VARIAVEL": "Apenas uma variável",
    "VAR_NAO_DEFINIDA": 2,
    "LISTA2": [10, 2, 5, 7]
}


class MyDocxTemplate(DocxTemplate):
    def render(
        self,
        context: Dict[str, Any],
        jinja_env: Optional[Environment] = None,
        autoescape: bool = False,
    ) -> None:
        # init template working attributes
        self.render_init()

        if autoescape:
            if not jinja_env:
                jinja_env = Environment(autoescape=autoescape)
            else:
                jinja_env.autoescape = autoescape

        # Body
        xml_src = self.build_xml(context, jinja_env)

        # fix tables if needed
        tree = self.fix_tables(xml_src)

        # fix docPr ID's
        self.fix_docpr_ids(tree)

        # Replace body xml tree
        self.map_tree(tree)

        # Headers
        headers = self.build_headers_footers_xml(
            context, self.HEADER_URI, jinja_env)
        for relKey, xml in headers:
            self.map_headers_footers_xml(relKey, xml)

        # Footers
        footers = self.build_headers_footers_xml(
            context, self.FOOTER_URI, jinja_env)
        for relKey, xml in footers:
            self.map_headers_footers_xml(relKey, xml)

        self.render_properties(context, jinja_env)

        self.render_footnotes(context, jinja_env)

        # set rendered flag
        self.is_rendered = True


tpl = MyDocxTemplate("template.docx")
tpl.render(context)

exit(0)

parts = []
for s in structures:
    parts.append(env.from_string(s).render(context))

with open("generated.xml", "w") as f:
    f.write("\n".join(parts))
