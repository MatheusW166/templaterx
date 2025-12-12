from docxtpl import DocxTemplate
from typing import IO, Dict, Any
from os import PathLike
from .helpers import jinja
from .structures import *

Context = Dict[str, Any]
TemplateFile = IO[bytes] | str | PathLike


class TemplaterX():
    def __init__(self, template_file: TemplateFile,) -> None:
        self._docx_template = DocxTemplate(template_file)
        self._jinja_env = jinja.get_environment()
        self._docx_components = DocxComponents()
        self._docx_template.render_init()

    @property
    def docx(self):
        docx = self._docx_template.docx
        if not docx:
            raise ValueError('No docx')
        return docx

    def save(self, filename: TemplateFile, *args, **kwargs) -> None:
        # Replacing original document

        # Body
        tree = self._docx_template.fix_tables(
            self._docx_components.to_clob("body")
        )
        self._docx_template.fix_docpr_ids(tree)
        self._docx_template.map_tree(tree)

        # Headers
        for relKey in self._docx_components.headers.keys():
            xml = self._docx_components.to_clob("headers", relKey)
            self._docx_template.map_headers_footers_xml(relKey, xml)

        # Footers
        for relKey in self._docx_components.footers.keys():
            xml = self._docx_components.to_clob("footers", relKey)
            self._docx_template.map_headers_footers_xml(relKey, xml)

        # Properties
        for prop in self._docx_components.properties.keys():
            xml = self._docx_components.to_clob("properties", prop)
            setattr(
                self.docx.core_properties,  # type: ignore
                prop,
                xml
            )

        # Footnotes
        self._get_footnotes()._blob = self._docx_components.to_clob(  # type: ignore
            "footnotes"
        ).encode(
            "utf-8"
        )

        return self._docx_template.save(filename, *args, **kwargs)

    def _get_footnotes(self):
        for section in self.docx.sections:
            if section.part.package is None:
                continue
            for part in section.part.package.parts:
                if part.content_type == (
                    "application/vnd.openxmlformats-officedocument"
                    ".wordprocessingml.footnotes+xml"
                ):
                    return part

    def _render_footnotes_partial_context(self, context: Context) -> list[Structure]:
        structures = self._docx_components.footnotes

        if not structures:
            footnotes = self._get_footnotes()

            if not footnotes:
                return []

            xml = footnotes.blob.decode("utf-8")
            structures = self._pre_process_xml(xml)

        return self._render_xml_part_partial_context(
            structures,
            context
        )

    def _render_properties_partial_context(self, context: Context):
        # List of string attributes of docx.opc.coreprops.CoreProperties which are strings.
        # It seems that some attributes cannot be written as strings. Those are commented out.
        properties = [
            "author",
            # 'category',
            "comments",
            # 'content_status',
            "identifier",
            # 'keywords',
            "language",
            # 'last_modified_by',
            "subject",
            "title",
            # 'version',
        ]

        for prop in properties:
            structures = self._docx_components.properties.get(prop, [])

            if not structures:
                xml = getattr(self.docx.core_properties, prop)
                structures = self._pre_process_xml(xml)

            structures = self._render_xml_part_partial_context(
                structures,
                context
            )
            yield prop, structures

    def _render_relitem_partial_context(self, uri: str, context: Context):
        for relKey, part in self._docx_template.get_headers_footers(uri):
            structures = self._docx_components.headers.get(relKey, [])

            if not structures:
                structures = self._pre_process_xml(
                    self._docx_template.get_part_xml(part)
                )

            structures = self._render_xml_part_partial_context(
                structures,
                context
            )

            for s in structures:
                if s.is_rendered:
                    s.clob = s.clob.encode("utf-8").decode("utf-8")

            yield relKey, structures

    def _pre_process_xml(self, xml: str):
        pre_processed_xml = self._docx_template.patch_xml(xml)
        return self._extract_complete_structures_from_xml(pre_processed_xml)

    def _render_body(self, context: Context):
        structures = self._docx_components.body

        if not structures:
            structures = self._pre_process_xml(self._docx_template.get_xml())

        return self._render_xml_part_partial_context(
            component_structures=structures,
            context=context
        )

    def _is_all_vars_in_context(self, template: str, context: Context):
        vars_from_template = self._extract_vars_from_xml(template)
        return len(vars_from_template - set(context.keys())) == 0

    def _extract_vars_from_xml(self, xml: str):
        return jinja.extract_jinja_vars_from_xml(xml)

    def _extract_complete_structures_from_xml(self, xml: str):
        return extract_jinja_structures_from_xml(xml)

    def _render_xml_part_partial_context(self, component_structures: list[Structure], context: Context):

        def render(structure: Structure):
            structure.clob = self._docx_template.render_xml_part(
                structure.clob,
                None,
                context,
                self._jinja_env
            )
            structure.is_rendered = True

        for structure in component_structures:
            if not structure.is_control_block:
                render(structure)
                continue

            if structure.is_rendered:
                continue

            if self._is_all_vars_in_context(structure.clob, context):
                render(structure)

        return component_structures

    def render_partial_context(
        self,
        context: Context
    ):

        # Body
        self._docx_components.body = self._render_body(context)

        # Headers
        for relKey, structures in self._render_relitem_partial_context(self._docx_template.HEADER_URI, context):
            self._docx_components.headers[relKey] = structures

        # Footers
        for relKey, structures in self._render_relitem_partial_context(self._docx_template.FOOTER_URI, context):
            self._docx_components.footers[relKey] = structures

        # Properties
        for prop, structures in self._render_properties_partial_context(context):
            self._docx_components.properties[prop] = structures

        # Footnotes
        self._docx_components.footnotes = self._render_footnotes_partial_context(
            context
        )

        self._docx_template.is_rendered = True
