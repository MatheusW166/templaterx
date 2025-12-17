from docxtpl import DocxTemplate
from typing import IO, Dict, Any, Optional
from os import PathLike
from .helpers import docxtpl, jinja
from .structures import *
from .docx_components import *
from jinja2 import Environment

Context = Dict[str, Any]
TemplateFile = IO[bytes] | str | PathLike


class TemplaterX():
    def __init__(self, template_file: TemplateFile, jinja_env: Optional[Environment] = None) -> None:
        self._jinja_env = jinja.get_keep_placeholders_environment(jinja_env)
        self._docx_template = DocxTemplate(template_file)
        self._docx_template.render_init()
        self._docx_components = DocxComponentsBuilder(
            self._docx_template
        ).build()

    @property
    def docx(self):
        docx = self._docx_template.docx
        if not docx:
            raise ValueError("No docx")
        return docx

    def _render_footnotes(self, context: Context):
        footnotes = self._docx_components.footnotes
        self._docx_components.footnotes = self._render_context(
            footnotes,
            context
        )

    def _render_properties(self, context: Context):
        props = self._docx_components.properties
        for prop in props:
            props[prop] = self._render_context(props[prop], context)

    def _render_relitem(self, component: RelItems, context: Context):
        part = self._docx_components[component]
        for relId in part:
            part[relId] = self._render_context(part[relId], context)

    def _render_body(self, context: Context):
        body = self._docx_components.body
        self._docx_components.body = self._render_context(body, context)

    def _extract_vars_from_xml(self, xml: str):
        return jinja.extract_jinja_vars_from_xml(xml)

    def _is_all_vars_in_context(self, template: str, context: Context):
        vars_from_template = self._extract_vars_from_xml(template)
        return len(vars_from_template - set(context.keys())) == 0

    def _render_context(self, component_structures: list[Structure], context: Context):

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

    def render(self, context: Context):

        self._render_body(context)
        self._render_relitem("headers", context)
        self._render_relitem("footers", context)
        self._render_properties(context)
        self._render_footnotes(context)

        self._docx_template.is_rendered = True

    def save(self, filename: TemplateFile, *args, **kwargs) -> None:
        # Replacing original document

        # Body
        tree = self._docx_template.fix_tables(
            self._docx_components.to_clob("body")
        )
        self._docx_template.fix_docpr_ids(tree)
        self._docx_template.map_tree(tree)

        # Headers
        for relKey in self._docx_components.headers:
            xml = self._docx_components.to_clob("headers", relKey)
            self._docx_template.map_headers_footers_xml(relKey, xml)

        # Footers
        for relKey in self._docx_components.footers:
            xml = self._docx_components.to_clob("footers", relKey)
            self._docx_template.map_headers_footers_xml(relKey, xml)

        # Properties
        for prop in self._docx_components.properties:
            xml = self._docx_components.to_clob("properties", prop)
            setattr(self.docx.core_properties, prop, xml)

        # Footnotes
        docxtpl.set_footnotes(
            self._docx_template,
            self._docx_components.to_clob("footnotes")
        )

        return self._docx_template.save(filename, *args, **kwargs)
