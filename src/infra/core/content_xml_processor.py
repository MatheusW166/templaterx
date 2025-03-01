import re
import copy
from lxml import etree as ET
from src.app.core.xml_processor_interface import XMLProcessorInterface

DEFAULT_NAMESPACES = {
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
}

class ContentXMLProcessor(XMLProcessorInterface):
    def __init__(self, element: bytes):
        self.namespaces = DEFAULT_NAMESPACES
        self.element: ET._Element = ET.fromstring(element)

    def _get_tables_by_name(self, name: str) -> list[ET._Element]:
        xpath_table = rf".//table:table[.//*[contains(text(), '%tr for d in {name}')]]"
        tables: list[ET._Element] = self.element.xpath(
            xpath_table,
            namespaces=self.namespaces
        )

        if len(tables) == 0:
            raise RuntimeError(f"No tables found for name '{name}'")

        return tables

    def _get_loop_delimiters(self, table: ET._Element) -> list[ET._Element]:
        xpath_loop_delimiters = r".//table:table-row[.//*[contains(text(),'%tr')]]"
        loop_delimiters = table.xpath(
            xpath_loop_delimiters,
            namespaces=self.namespaces
        )

        if len(loop_delimiters) == 0:
            raise RuntimeError("Loop delimiters not found")

        return loop_delimiters

    def _get_row_template(self, table: ET._Element) -> ET._Element:
        xpath_row_template = r".//table:table-row[.//*[contains(text(),'d.')]]"
        row_template = table.xpath(
            xpath_row_template,
            namespaces=self.namespaces
        )

        if len(row_template) == 0:
            raise RuntimeError("Row template not found")

        return row_template[0]

    def _get_row_template_attributes(self, row_template: ET._Element) -> list[ET._Element]:
        xpath_column = r".//*[contains(text(),'d.')]"
        row_template_attributes = row_template.xpath(
            xpath_column,
            namespaces=self.namespaces
        )

        if len(row_template_attributes) == 0:
            raise RuntimeError("Row template columns not found")

        return row_template_attributes

    def _get_attribute_from_text(self, textContent: str):
        match = re.search(r"d\.(\w+)", textContent)

        if match is None:
            raise RuntimeError(f"No attribute found in '{textContent}'")

        return match.group(1)

    def _append_data_rows(self, row_template: ET._Element, data: list[dict] = []):
        previous = row_template

        for d in data:
            row_cp: ET._Element = copy.deepcopy(row_template)

            for el in self._get_row_template_attributes(row_cp):
                key = self._get_attribute_from_text(el.text)
                value = d.get(key, Exception())

                if isinstance(value, Exception):
                    raise RuntimeError(
                        f"No sql column found for attribute 'd.{key}'")

                el.text = str(value)

            previous.addnext(row_cp)
            previous = row_cp

    def _remove_all(self, *elements: ET._Element):
        for e in elements:
            e.getparent().remove(e)

    def find_tables(self) -> list[str]:
        return list(set(re.findall(r"<table:table.*? in (\w+)", self.tostring())))

    def build_tables_with_name(self, name: str,   data: list[dict] = []):
        if len(data) == 0:
            return

        # Get all tables with the same name
        tables = self._get_tables_by_name(name)

        for table in tables:
            row_template = self._get_row_template(table)

            self._append_data_rows(row_template, data)

            loop_delimiters = self._get_loop_delimiters(table)
            self._remove_all(row_template, *loop_delimiters)

    def tostring(self) -> str:
        return ET.tostring(self.element)
