from pathlib import Path
from templaterx import TemplaterX, DocxComponentsBuilder
from docxtpl import DocxTemplate
import zipfile
import re


def get_rendered_xml(tplx: TemplaterX, tmp_path: Path, skip_pre_process=True) -> str:

    # Avoid saving twice
    if not tmp_path.is_file():
        tplx.save(tmp_path)

    def build_docxtpl(tpl_path):
        docxtpl = DocxTemplate(tpl_path)
        docxtpl.render_init()
        return docxtpl

    cmp = DocxComponentsBuilder(
        docx_template=build_docxtpl(tmp_path),
        jinja_env=tplx._jinja_env,
        skip_pre_process=skip_pre_process
    ).build()

    all_public_properties_xml = "\n".join([
        cmp.to_clob(p)  # type: ignore
        for p in cmp.__dict__.keys()
        if not re.match(r"_.*", p)
    ])

    return all_public_properties_xml


def generate_xml_file(tplx: TemplaterX, tmp_path: Path):
    with open("content.xml", "w") as f:
        f.write(get_rendered_xml(tplx, tmp_path))


def read_embedded_bytes(docx_path: Path, embedded_name: str):
    with zipfile.ZipFile(docx_path) as z:
        return z.read(embedded_name)


def extract_all_embedded_docx_files(docx_path: Path, tmp_path: Path) -> list[Path]:
    """
    Extracts embedded OLE objects that are DOCX files and returns paths to them.
    """
    extracted = []

    with zipfile.ZipFile(docx_path) as z:
        for name in z.namelist():
            if name.endswith(".docx"):
                data = z.read(name)

                if data.startswith(b"PK"):
                    out = tmp_path / Path(name).name.replace(".bin", ".docx")
                    out.write_bytes(data)
                    extracted.append(out)

    return extracted


def extract_all_images(docx_path: Path, tmp_path: Path) -> list[Path]:
    from time import time

    extracted: list[Path] = []

    def get_tmp_path(name: str):
        return tmp_path / f"{time()}_{Path(name).name}"

    with zipfile.ZipFile(docx_path) as z:
        for name in z.namelist():
            if name.startswith("word/media/image"):
                data = z.read(name)
                out = get_tmp_path(name)

                while out.is_file():
                    out = get_tmp_path(name)

                out.write_bytes(data)
                extracted.append(out)

    return extracted
