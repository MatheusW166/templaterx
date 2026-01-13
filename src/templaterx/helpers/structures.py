from jinja2 import Environment
from ..structure import Structure
from ..exceptions import TemplateError
from typing import cast
from . import jinja
import re


def extract_vars_from_structures(structures: list[Structure], jinja_env: Environment | None = None):
    for s in structures:
        yield jinja.extract_jinja_vars_from_xml(s.clob, jinja_env)


def control_blocks_var_adjacency_map(structures: list[Structure], prev: dict[str, set[str]]) -> dict[str, set[str]]:
    """
    Builds an adjacency map of Jinja2 template variables based on their
    co-occurrence within the provided control blocks.

    ### Example input::

        {%for d in LIST%}
            {{d}}
            {% if VAR1 %}
                COND1
            {% endif %}
            {% if VAR2 %}
                COND2
            {% endif %}
        {% endfor %}

    ### Example output::

        {
            "LIST": {"VAR1","VAR2"},
            "VAR1": {"LIST","VAR2"},
            "VAR2": {"LIST","VAR1"}
        }
    """

    for structure in structures:

        if not structure.is_control_block:
            continue

        extracted_vars = jinja.extract_jinja_vars_from_xml(structure.clob)

        if not extracted_vars:
            continue

        for var in extracted_vars:
            existing = prev.get(var, set())
            prev[var] = existing | (extracted_vars - {var})

    return prev


def collect_control_blocks_connected_vars(start_var: str, control_blocks_var_adjacency_map: dict[str, set[str]]):
    stack = [start_var]
    result: set[str] = set()

    while stack:
        var = stack.pop()

        if var in result:
            continue

        result.add(var)

        for neighbor in control_blocks_var_adjacency_map.get(var, ()):
            if neighbor in result:
                continue
            stack.append(neighbor)

    return result


def extract_jinja_structures_from_xml(xml: str) -> list[Structure]:
    """
    Extract Jinja2 structures from a given XML string, returning a list of
    Structure objects.

    ### Important:
        Control block delimiters must be outside XML tags to be detected properly. Make sure 
        to make all pre-processing needed to ensure this before using this function.

    #### Right input example::

        {% for item in LIST %}
        <w:t>{{ item }}</w:t>
        {% endfor %}

    #### Wrong input example::

        <w:t>
            <w:tr>
                {% for item in LIST %}
            <w:tr/>
            <w:tr>{{ item }}</w:tr>
            <w:tr>
                {% endfor %}
            </w:tr>
        <w:t/>
    """

    control_block_pattern = r"(\{\%.*?\%\})"
    tokens: list[str] = re.split(
        control_block_pattern,
        xml,
        flags=re.DOTALL
    )

    # Anything like {% (for|if|raw)...%}
    open_pattern = r"\{\%\s*(for|if|raw)\s.*?\%\}"

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
                raise TemplateError(
                    f"Reserved word not found for '{open_block}'"
                )

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
            raise TemplateError(
                f"Open block not found for '{current_structure}'"
            )

        if close_block_expected_stack[-1] in close_block:
            close_block_expected_stack.pop()

        if not close_block_expected_stack:
            finish_current_structure(is_control_block=True)

    if close_block_expected_stack:
        raise TemplateError(
            f"Those close blocks were not found: {close_block_expected_stack}"
        )

    return structures
