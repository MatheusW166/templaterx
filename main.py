from jinja2 import Environment, meta
from templaterx.engine import TemplaterX


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


context = {
    "LISTA": ["A", "B", "C"],
    "VARIAVEL": "Apenas uma variável",
    "VARIAVEL2": "COLOQUEI NO FOOTNOTE",
    "LIVRE": "Var livre",
    "VAR_NAO_DEFINIDA": 2,
}

tplx = TemplaterX("_template.docx")
tplx.render_partial_context(context)
tplx.save("_generated.docx")
