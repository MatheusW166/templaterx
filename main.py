from templaterx import TemplaterX


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
