from docxtpl import DocxTemplate
from jinja2 import Environment
from typing import IO, Any, Dict, cast
from pathlib import Path
from .helpers import docx, jinja
from .structure import Structure
from .components import DocxComponentsBuilder, RelItems
from .types import DocxPartType, DocumentType, TemplateSource, Context


class TemplaterX():
    def __init__(
        self,
        template_file: TemplateSource,
        jinja_env: Environment | None = None,
        autoescape=False,
    ) -> None:
        self._template_file = template_file
        self._jinja_env = jinja.get_keep_placeholders_environment(
            jinja_env,
            autoescape
        )
        self.init_state()

    def init_state(self):
        tpl = DocxTemplate(self._template_file)
        tpl.render_init()
        self._docx_template = tpl
        self._docx_components = DocxComponentsBuilder(
            tpl,
            self._jinja_env
        ).build()
        self.current_rendering_part: DocxPartType | None = None
        self._use_docxtpl_renderer = False

    def build_url_id(self, url: DocxPartType | str):
        return self._docx_template.build_url_id(url)

    def new_subdoc(self, docpath: str | IO[bytes] | None = None) -> DocumentType:
        return cast(DocumentType, self._docx_template.new_subdoc(docpath=docpath))

    def replace_embedded(self, src: Path, dst: Path):
        return self._docx_template.replace_embedded(src_file=src, dst_file=dst)

    def replace_zipname(self, zipname: str, dst: Path):
        return self._docx_template.replace_zipname(zipname=zipname, dst_file=dst)

    def replace_media(self, src: Path | IO[bytes], dst: Path | IO[bytes]):
        return self._docx_template.replace_media(src_file=src, dst_file=dst)

    def replace_pic(self, pic_in_docx_name: str, dst: Path | IO[bytes]):
        return self._docx_template.replace_pic(embedded_file=pic_in_docx_name, dst_file=dst)

    def get_undeclared_template_variables(self, context: Dict[str, Any] | None = None):
        return self._docx_template.get_undeclared_template_variables(self._jinja_env, context)

    def _render_relitem(self, component: RelItems, context: Context):
        relItems = self._docx_components[component]
        for relId in relItems:
            part = self._docx_components.get_part(component, relKey=relId)
            relItems[relId] = self._render_context(
                relItems[relId],
                context,
                part
            )

    def _render_footnotes(self, context: Context):
        footnotes = self._docx_components.footnotes
        part = self._docx_components.get_part("footnotes")
        self._docx_components.footnotes = self._render_context(
            footnotes,
            context,
            part
        )

    def _render_body(self, context: Context):
        body = self._docx_components.body
        part = self._docx_components.get_part("body")
        self._docx_components.body = self._render_context(body, context, part)

    @classmethod
    def _is_all_vars_in_context(cls, template: str, context: Context):
        vars_from_template = jinja.extract_jinja_vars_from_xml(template)
        return len(vars_from_template - set(context.keys())) == 0

    def _render_context(
        self,
        component_structures: list[Structure],
        context: Context,
        part: DocxPartType | None
    ):
        self.current_rendering_part = part

        def render_with_docxtpl(structure: Structure):
            structure.clob = self._docx_template.render_xml_part(
                structure.clob,
                part,
                context,
                self._jinja_env
            )

        def render_with_jinja2(structure: Structure):
            engine = self._jinja_env.from_string(structure.clob)
            structure.clob = engine.render(context)

        def render(structure: Structure):
            renderer = render_with_jinja2

            if self._use_docxtpl_renderer:
                renderer = render_with_docxtpl

            renderer(structure)
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

    def render(self, context: Context, use_docx_tpl_renderer=False):
        self._use_docxtpl_renderer = use_docx_tpl_renderer

        self._render_body(context)
        self._render_relitem("headers", context)
        self._render_relitem("footers", context)
        self._render_footnotes(context)

        self._docx_template.is_rendered = True

    def save(self, filename: TemplateSource, *args, **kwargs) -> TemplateSource:
        # Before save
        self.render({}, use_docx_tpl_renderer=True)

        # Replacing original document

        tree = self._docx_template.fix_tables(
            self._docx_components.to_clob("body")
        )
        self._docx_template.fix_docpr_ids(tree)
        self._docx_template.map_tree(tree)

        for relKey in self._docx_components.headers:
            xml = self._docx_components.to_clob("headers", relKey)
            self._docx_template.map_headers_footers_xml(relKey, xml)

        for relKey in self._docx_components.footers:
            xml = self._docx_components.to_clob("footers", relKey)
            self._docx_template.map_headers_footers_xml(relKey, xml)

        docx.set_footnotes(
            self._docx_template.docx,
            self._docx_components.to_clob("footnotes")
        )

        self._docx_template.save(filename, *args, **kwargs)
        self.init_state()

        return filename
