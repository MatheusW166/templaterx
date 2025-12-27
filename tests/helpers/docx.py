from docx import Document
from pathlib import Path
from src.templaterx import TemplaterX


def extract_text(docx_path: str) -> str:
    doc = Document(docx_path)
    return "\n".join(p.text for p in doc.paragraphs)


def save_and_get_text(tplx: TemplaterX, tmp_path: Path) -> str:
    tplx.save(tmp_path)
    return extract_text(str(tmp_path))
