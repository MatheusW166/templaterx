from dataclasses import dataclass
import zipfile
import re
from lxml import etree as ET
import copy

orig_file = "template.odt"
generated_file = "_generated_doc.odt"


@dataclass
class XMLElementCustom(ET._Element):
    def __init__(self, *args, **kwargs):
        self.namespaces = {
            'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
            'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
            'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
        }
        super().__init__(*args, **kwargs)

    def xpath(self, path: str):
        super().xpath(path, namespaces=self.namespaces)


def create_no_content_copy(orig_file: str, generated_file: str):
    with zipfile.ZipFile(orig_file, "r") as zip_read:
        with zipfile.ZipFile(generated_file, "w", zipfile.ZIP_DEFLATED) as zip_write:
            for item in zip_read.infolist():
                if item.filename != "content.xml":  # Ignorar o content.xml antigo
                    zip_write.writestr(
                        item.filename, zip_read.read(item.filename))


def generate_document(content_xml: str):
    # Criar novo arquivo .odt
    create_no_content_copy(orig_file, generated_file)

    # Adicionar conteúdo modificado
    with zipfile.ZipFile(generated_file, "a") as zip_mod:
        zip_mod.writestr("content.xml", content_xml)

    print(f"Arquivo modificado salvo como: {generated_file}")


def load_contentxml() -> ET._Element:
    with zipfile.ZipFile(orig_file, "r") as files:
        return ET.fromstring(files.read("content.xml"))


def fill_tables_by_name(name: str, content_xml: ET._Element, data: list[dict] = []):
    if len(data) == 0:
        return

    namespaces = {
        'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
        'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
        'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
    }

    xpath_table = rf".//table:table[.//*[contains(text(), '%tr for d in {name}')]]"
    xpath_loop_delimiters = r".//table:table-row[.//*[contains(text(),'%tr')]]"
    xpath_row_template = r".//table:table-row[.//*[contains(text(),'d.')]]"
    xpath_column = r".//*[contains(text(),'d.')]"

    tables: list[ET._Element] = content_xml.xpath(
        xpath_table,
        namespaces=namespaces
    )

    # In case of multiple tables with the same name are found, all of them will be filled
    for table in tables:
        rows_loop_delimiters: list[ET._Element] = table.xpath(
            xpath_loop_delimiters,
            namespaces=namespaces
        )
        row_template: ET._Element = table.xpath(
            xpath_row_template,
            namespaces=namespaces
        )[0]

        previous = row_template
        for d in data:
            row_cp: ET._Element = copy.deepcopy(row_template)

            for column in row_cp.xpath(xpath_column, namespaces=namespaces):
                key = re.search(r"d\.(\w+)", column.text).group(1)
                column.text = d.get(key, f"'d.{key}' not found")

            previous.addnext(row_cp)
            previous = row_cp

        row_template.getparent().remove(row_template)
        for r in rows_loop_delimiters:
            r.getparent().remove(r)

    return content


content = load_contentxml()

fill_tables_by_name("DADOS_CORREICAO", content, [{"NOME": "ALGO", "IDADE": 1}])

generate_document(ET.tostring(content))

# fill_table("PERIODO_PRAZO_TIPO", content, [["ALGO"], [1]])
