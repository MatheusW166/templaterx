from docxtpl import DocxTemplate
from typing import TypeAlias, IO, Any, Optional, Mapping
from os import PathLike
from .helpers import docxtpl, jinja
from .structures import *
from .docx_components import *
from jinja2 import Environment

Context: TypeAlias = Mapping[str, Any]
TemplateFile: TypeAlias = IO[bytes] | str | PathLike


class TemplaterX():
    def __init__(self, template_file: TemplateFile, jinja_env: Optional[Environment] = None) -> None:
        tpl = DocxTemplate(template_file)
        tpl.render_init()
        jja_custom = jinja.get_keep_placeholders_environment(jinja_env)
        self._docx_components = DocxComponentsBuilder(tpl, jja_custom).build()
        self._jinja_env = jja_custom
        self._docx_template = tpl

    @property
    def components(self):
        return self._docx_components

    def _render_relitem(self, component: RelItems, context: Context):
        part = self.components[component]
        for relId in part:
            part[relId] = self._render_context(part[relId], context)

    def _render_footnotes(self, context: Context):
        footnotes = self.components.footnotes
        self.components.footnotes = self._render_context(
            footnotes,
            context
        )

    def _render_body(self, context: Context):
        body = self.components.body
        self.components.body = self._render_context(body, context)

    def _is_all_vars_in_context(self, template: str, context: Context):
        vars_from_template = jinja.extract_jinja_vars_from_xml(template)
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
        self._render_footnotes(context)

        self._docx_template.is_rendered = True

    def save(self, filename: TemplateFile, *args, **kwargs) -> None:
        # Replacing original document

        tree = self._docx_template.fix_tables(
            self.components.to_clob("body")
        )
        self._docx_template.fix_docpr_ids(tree)
        self._docx_template.map_tree(tree)

        for relKey in self.components.headers:
            xml = self.components.to_clob("headers", relKey)
            self._docx_template.map_headers_footers_xml(relKey, xml)

        for relKey in self.components.footers:
            xml = self.components.to_clob("footers", relKey)
            self._docx_template.map_headers_footers_xml(relKey, xml)

        docxtpl.set_footnotes(
            self._docx_template,
            self.components.to_clob("footnotes")
        )

        return self._docx_template.save(filename, *args, **kwargs)
