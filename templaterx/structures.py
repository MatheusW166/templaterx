from dataclasses import dataclass
from typing import cast
import re


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


def extract_jinja_structures_from_xml(xml: str):
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
