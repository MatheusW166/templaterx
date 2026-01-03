from pathlib import Path
from src.templaterx import TemplaterX
import re


def get_rendered_xml(tplx: TemplaterX, tmp_path: Path) -> str:
    tplx.save(tmp_path)

    cmp = TemplaterX(tmp_path, tplx._jinja_env).components

    all_public_properties_xml = "\n".join([
        cmp.to_clob(p)  # type: ignore
        for p in cmp.__dict__.keys()
        if not re.match(r"_.*", p)
    ])

    return all_public_properties_xml
