from pathlib import Path
from src.templaterx import TemplaterX, DocxComponentsBuilder
import zipfile
import re


def get_rendered_xml(tplx: TemplaterX, tmp_path: Path) -> str:
    tplx.save(tmp_path)

    docx_components = DocxComponentsBuilder(
        tplx._docx_template,
        jinja_env=tplx._jinja_env,
        skip_pre_process=True
    ).build()

    cmp = TemplaterX(
        template_file=tmp_path,
        jinja_env=tplx._jinja_env,
        docx_components=docx_components
    ).components

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
    extracted: list[Path] = []

    with zipfile.ZipFile(docx_path) as z:
        for name in z.namelist():
            if name.startswith("word/media/image"):
                data = z.read(name)
                out = tmp_path / Path(name).name
                out.write_bytes(data)
                extracted.append(out)

    return extracted
