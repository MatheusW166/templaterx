import re
import copy
import lxml as ET
from src.app.core.xml_processor_interface import XMLProcessorInterface
from src.infra.shared.logs import Logger


DEFAULT_NAMESPACES = {
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
}

logs = Logger.get_logger()


class ContentXMLProcessor(XMLProcessorInterface):
    def __init__(self, element: bytes):
        self.namespaces = DEFAULT_NAMESPACES
        self.element: ET._Element = ET.fromstring(element)

    # LAST ROW VARS
    def _find_all_last_row_vars(self, string: str):
        return re.findall(r"(\w+)\s*\|\s*ultima_linha", string, flags=re.IGNORECASE)

    def _get_last_row_vars_by_name(self, name: str) -> list[ET._Element]:
        xpath_last_row_vars = rf"""
            .//text:span[contains(
                translate(
                    translate(string(), ' ', ''), 
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'
                ),
                '{name.strip().lower()}|ultima_linha'
            )]
        """

        last_row_vars = self.element.xpath(
            xpath_last_row_vars,
            namespaces=self.namespaces
        )

        return last_row_vars

    def _get_attribute_from_last_row_var_text(self, textContent: str):
        match = re.search(r"\)\.(\w+)", textContent)

        if match is None:
            raise RuntimeError(f"No attribute found in '{textContent}'")

        return match.group(1)

    def _fill_last_row_vars_with_name(self, name: str, last_row: dict):
        last_row_vars = self._get_last_row_vars_by_name(name)

        for last_row_var in last_row_vars:
            text_content = self._get_text_content(last_row_var)

            if not text_content:
                continue

            key = self._get_attribute_from_last_row_var_text(text_content)
            value = last_row.get(key, Exception())

            if isinstance(value, Exception):
                logs.warning(f"No sql col found for attribute 'd.{key}'")
                continue

            filled_text_content = re.sub(
                r"\{\{.*?\}\}",
                str(value) if value is not None else "-",
                text_content
            )
            self._replace_element_content(last_row_var, filled_text_content)

    # TABLES
    def _find_all_tables(self, string: str):
        return re.findall(r"<table:table.*? in (\w+)", string, flags=re.IGNORECASE)

    def _get_tables_by_name(self, name: str) -> list[ET._Element]:
        string_search = f"""
            contains(translate(string(),' ',''), '%trfordin{name.strip()}%')
        """
        xpath_table = rf".//table:table[.//*[{string_search}]]"
        tables: list[ET._Element] = self.element.xpath(
            xpath_table,
            namespaces=self.namespaces
        )

        return tables

    def _get_loop_delimiters_or_raise(self, table: ET._Element) -> list[ET._Element]:
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

    def _get_attribute_from_table_text(self, textContent: str):
        match = re.search(r"d\.(\w+)", textContent)

        if match is None:
            raise RuntimeError(f"No attribute found in '{textContent}'")

        return match.group(1)

    def _append_data_row(self, row_template: ET._Element, data_row: dict):
        previous = row_template

        row_cp: ET._Element = copy.deepcopy(row_template)

        for el in self._get_row_template_attributes(row_cp):
            text_content = self._get_text_content(el)
            key = self._get_attribute_from_table_text(text_content)
            value = data_row.get(key, Exception())

            if isinstance(value, Exception):
                logs.warning(f"No sql col found for attribute 'd.{key}'")
                continue

            self._replace_element_content(
                el,
                str(value) if value is not None else "-"
            )

        previous.addnext(row_cp)
        previous = row_cp

    def _fill_tables_with_name(self, name: str,   data: list[dict] = []):
        tables = self._get_tables_by_name(name)

        for table in tables:
            loop_delimiters = self._get_loop_delimiters_or_raise(table)

            row_template = self._get_row_template(table)
            for data_row in data:
                self._append_data_row(row_template, data_row)

            self._remove_all(row_template, *loop_delimiters)

    # GENERIC

    def _replace_element_content(self, element: ET._Element, value: str):
        self._remove_all(*element.getchildren())
        element.text = value

    def _get_text_content(self, element: ET._Element) -> str:
        result = element.xpath("string()", namespaces=DEFAULT_NAMESPACES)
        return result.strip() if isinstance(result, str) else None

    def _remove_all(self, *elements: ET._Element):
        for e in elements:
            parent = e.getparent()
            if isinstance(parent, ET._Element):
                parent.remove(e)

    def find_all_vars(self) -> list[str]:
        strigfied_content = self.tostring()
        return list({
            *self._find_all_last_row_vars(strigfied_content),
            *self._find_all_tables(strigfied_content)
        })

    def tostring(self) -> str:
        return ET.tostring(self.element, encoding="unicode")

    def fill_content(self, name: str, data: list[dict] = []):
        logs.info(f"{name}: Filling content")

        if len(data) == 0:
            logs.warning(f"{name}: No data to fill")
            return

        data_reversed = data[::-1]

        self._fill_tables_with_name(name, data_reversed)
        self._fill_last_row_vars_with_name(name, data_reversed[0])
