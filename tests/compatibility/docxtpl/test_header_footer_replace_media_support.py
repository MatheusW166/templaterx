from templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx, hash as hs
from tests.helpers.faker import faker_pt_BR as faker
import io
import pytest


@pytest.fixture
def paths(tmp_path):
    templates = [
        "header_footer_image_tpl.docx",
        "dummy_pic_for_header.png",
        "python.png",
    ]

    return {
        name: p.Paths(
            template=TEMPLATES_DIR / name,
            out=tmp_path / f"{name.replace('.', '_')}_out.docx",
        )
        for name in templates
    }


def test_replace_media_should_work_in_header_and_footer(paths, tmp_path):
    rendered_file_path = paths["header_footer_image_tpl.docx"]
    tplx = TemplaterX(rendered_file_path.template)

    dummy_image = paths["dummy_pic_for_header.png"].template
    new_image = paths["python.png"].template

    tplx.replace_media(dummy_image, new_image)

    context = {"mycompany": faker.company()}

    tplx.render(context)
    tplx.save(rendered_file_path.out)

    rendered_doc_images = docx.extract_all_images(
        rendered_file_path.out,
        tmp_path
    )
    rendered_doc_image = rendered_doc_images[0]

    assert len(rendered_doc_images) == 1
    assert hs.file_hash(rendered_doc_image) == hs.file_hash(new_image)

    xml = docx.get_rendered_xml(tplx, rendered_file_path.out)
    assert context["mycompany"] in xml


def test_replace_media_should_work_in_header_and_footer_with_bytes_stream(paths, tmp_path):
    rendered_file_path = paths["header_footer_image_tpl.docx"]
    tplx = TemplaterX(rendered_file_path.template)

    dummy_pic = io.BytesIO(
        open(paths["dummy_pic_for_header.png"].template, "rb").read()
    )
    new_image = io.BytesIO(
        open(paths["python.png"].template, "rb").read()
    )
    tplx.replace_media(dummy_pic, new_image)

    context = {"mycompany": faker.company()}

    tplx.render(context)
    tplx.save(rendered_file_path.out)

    rendered_doc_images = docx.extract_all_images(
        rendered_file_path.out,
        tmp_path
    )
    rendered_doc_image = rendered_doc_images[0]

    assert len(rendered_doc_images) == 1

    new_image.seek(0)
    assert hs.file_hash(rendered_doc_image) == hs.bytes_hash(new_image.read())

    xml = docx.get_rendered_xml(tplx, rendered_file_path.out)
    assert context["mycompany"] in xml

    # tpl = DocxTemplate("templates/header_footer_image_tpl.docx")
    # dummy_pic.seek(0)
    # new_image.seek(0)
    # tpl.replace_media(dummy_pic, new_image)
    # tpl.render(context)

    # file_obj = io.BytesIO()
    # tpl.save(file_obj)
    # file_obj.seek(0)
    # with open(DEST_FILE2, "wb") as f:
    #     f.write(file_obj.read())
