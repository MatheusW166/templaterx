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

print(vars)

# env = Environment(trim_blocks=True)

# rendered = env.from_string(clob).render(
#     {"LISTA": ["A", "B", "C"], "VAR_NAO_DEFINIDA": 1})
# print(rendered)
