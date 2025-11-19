from jinja2 import Undefined, Environment, meta
import re
from typing import cast
from docxtpl import DocxTemplate

# # First render
# doc = DocxTemplate("template.docx")
# doc.render({
#     "LISTA": ["A","B","C"],
# })

# # Second render
# doc.render({
#      "LISTA2": ["A","B","C"],
# })

# doc.save("_generated.docx")

# exit(0)


def match(pattern: str, text: str, group=0):
    m = re.match(pattern, text, flags=re.DOTALL)

    if m:
        try:
            return cast(str, m.group(group))
        except:
            pass

    return None


def extract_complete_structures(xml: str):
    tokens: list[str] = re.split(r"(\{\%.*?\%\})", xml, flags=re.DOTALL)

    # Anything like {%...%} without "end"
    open_pattern = r"\{\%\s*(?!.*end).*?\%\}"

    # Anything like {% end... %}
    close_pattern = r"\{\%\s*end.*?\%\}"

    # Gets the reserved word, example:
    # {% for... %} => for, {% if... %} => if
    reserved_word_pattern = r"\{\%\s*(\S+)"

    close_block_stack: list[str] = []
    structures: list[str] = []
    structure = ""

    for token in tokens:
        open_block = match(open_pattern, token)

        if open_block:
            structure += open_block
            reserved_word = match(reserved_word_pattern, open_block, 1)

            if not reserved_word:
                raise RuntimeError(open_block)

            end_block = "end"+reserved_word
            close_block_stack.append(end_block)
            continue

        close_block = match(close_pattern, token)
        if not close_block:
            structure += token
            continue

        if not close_block_stack:
            raise RuntimeError("No open block found\n"+structure)

        if close_block_stack[-1] in close_block:
            structure += close_block
            close_block_stack.pop()

        if not close_block_stack:
            structures.append(structure.strip())
            structure = ""
    else:
        structures[-1] += tokens[-1]

    return structures


"""
TODO:
Problema => dada uma variável, quais as outras que devo consultar para
renderizar todos os blocos em que ela aparece? E quais os indíces desses blocos?
"""


def index_vars_in_structures(structures: list[str]):

    from time import time
    s = time()

    env = Environment()

    def get_vars(xml: str):
        parsed = env.parse(xml)
        return meta.find_undeclared_variables(parsed)

    for idx, structure in enumerate(structures):
        vars = get_vars(structure)
        print(vars)

    print(time() - s)


class KeepVarUndefined(Undefined):
    """
    Keeps {{ ... }} untouched if it's not found in the context dict
    """

    def __str__(self):
        return f"{{{{ {self._undefined_name} }}}}"

    def __getattr__(self, name):
        return f"{{{{ {self._undefined_name}.{name} }}}}"

    def __getitem__(self, key):
        return f"{{{{ {self._undefined_name}['{key}'] }}}}"


with open("pre-processed.xml", "r") as f:
    clob = f.read()

structures = extract_complete_structures(clob)

index_vars_in_structures(structures)

exit(0)

env = Environment(trim_blocks=True, undefined=KeepVarUndefined)

rendered = env.from_string(result[0]).render(
    {"LISTA": ["A", "B", "C"], "VAR_NAO_DEFINIDA": 1})
print(rendered)
