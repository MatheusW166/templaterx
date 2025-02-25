import zipfile
import re

orig_file = "template.odt"
generated_file = "_generated_doc.odt"


def fill_table(name: str, content_xml: str, data=[]):
    table_match = list(re.finditer(rf"<table:table.*?{name}.*?</table:table>", content_xml))[0]
    row_match = list(re.finditer(r"<table:table-row.*?</table:table-row>", table_match.group()))

    row_match_data = row_match[-2]

    row_template = row_match_data.group()
    rows = ""

    columns = data[0]
    for d in data[1:]:
        row = row_template
        for i, v in enumerate(d):
            var = "{{" + f" d.{columns[i]} " + "}}"
            row = row.replace(var, v)
        rows += row

    ini, end = row_match[1].span()[0], row_match[-1].span()[1]
    table = table_match.group()[:ini] + rows + table_match.group()[end:]

    ini, end = table_match.span()
    return content_xml[:ini] + table + content_xml[end:]


def create_no_content_copy(orig_file: str, generated_file: str):
    with zipfile.ZipFile(orig_file, "r") as zip_read:
        with zipfile.ZipFile(generated_file, "w", zipfile.ZIP_DEFLATED) as zip_write:
            for item in zip_read.infolist():
                if item.filename != "content.xml":  # Ignorar o content.xml antigo
                    zip_write.writestr(
                        item.filename, zip_read.read(item.filename))


create_no_content_copy(orig_file, generated_file)

# Dados a serem inseridos
data = [
    ["inicio", "fim", "egestao_inicio", "egestao_fim", "vara"],
    ["2024-01-01", "2024-12-31", "2025-12-24", "2026-05-01", "1ª Vara Federal de São Paulo"],
    ["2027-05-15", "2028-10-30", "2021-01-01", "2022-12-31", "2ª Vara Federal de São Paulo"]
]

with zipfile.ZipFile(orig_file, "r") as files:
    content = files.read("content.xml").decode()

content = fill_table("DADOS_CORREICAO", content, data)

# Adicionar o novo content.xml ao ODT
with zipfile.ZipFile(generated_file, "a") as zip_mod:
    zip_mod.writestr("content.xml", content)

print(f"Arquivo modificado salvo como: {generated_file}")
