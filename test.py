import zipfile
import re

orig_file = "template.odt"
generated_file = "_generated_doc.odt"


def load_contentxml():
    with zipfile.ZipFile(orig_file, "r") as files:
        return files.read("content.xml").decode()


def fill_table(name: str, content_xml: str, data=[]):

    
    table_match = re.search(
        rf"<table:table[\s\S]*?{name}[\s\S]*?</table:table>", content_xml)

    print(table_match.group())
    exit(0)
    row_match = list(re.finditer(
        r"<table:table-row.*?</table:table-row>", table_match.group()))

    row_match_data = row_match[-2]

    row_template = row_match_data.group()
    rows = ""

    columns = data[0]
    for d in data[1:]:
        row = row_template
        for i, v in enumerate(d):
            var = "{{" + f" d.{columns[i]} " + "}}"
            row = row.replace(var, str(v or ""))
        rows += row

    # Ajustar lógica, pois nem sempre a linha 1 é a linha que contém {{%tr for ... %}}
    ini, end = row_match[1].span()[0], row_match[-1].span()[1]
    table = table_match.group()[:ini] + rows + table_match.group()[end:]

    ini, end = table_match.span()
    return content_xml[:ini] + table + content_xml[end:]


content = load_contentxml()

fill_table("PERIODO_PRAZO_TIPO", content, [["ALGO"], [1]])


def create_no_content_copy(orig_file: str, generated_file: str):
    with zipfile.ZipFile(orig_file, "r") as zip_read:
        with zipfile.ZipFile(generated_file, "w", zipfile.ZIP_DEFLATED) as zip_write:
            for item in zip_read.infolist():
                if item.filename != "content.xml":  # Ignorar o content.xml antigo
                    zip_write.writestr(
                        item.filename, zip_read.read(item.filename))
