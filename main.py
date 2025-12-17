from templaterx import TemplaterX
from templaterx.helpers import jinja


def index_vars_in_structures(structures: list[str]):
    vars_per_structure: list[set[str]] = [set() for _ in structures]
    cooccurrence_map: dict[str, set[str]] = {}

    for structure_index, template in enumerate(structures):
        extracted_vars = jinja.extract_jinja_vars_from_xml(template)

        if not extracted_vars:
            continue

        vars_per_structure[structure_index] |= extracted_vars

        for var in extracted_vars:
            existing = cooccurrence_map.get(var, set())
            cooccurrence_map[var] = existing | (extracted_vars - {var})

    return vars_per_structure, cooccurrence_map


def collect_connected_vars(start_var: str, cooccurrence_map: dict[str, set[str]]):
    stack = [start_var]
    result: set[str] = set()

    while stack:
        var = stack.pop()

        if var in result:
            continue

        result.add(var)

        for neighbor in cooccurrence_map.get(var, ()):
            if neighbor not in result:
                stack.append(neighbor)

    return result


context = {
    "LISTA": ["A", "B", "C"],
    "VARIAVEL": "Apenas uma variável",
    "VARIAVEL2": "COLOQUEI NO FOOTNOTE",
    "LIVRE": "Var livre",
}

tplx = TemplaterX("_template.docx")
tplx.render(context)
tplx.render(context={
    "LISTA": ["A", "B", "C"],
    "VAR_NAO_DEFINIDA": 3,
})
tplx.save("_generated.docx")
