import pytest
from dataclasses import dataclass
from src.templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from ..helpers import docx, paths as p
from ..helpers.faker import faker_pt_BR as faker


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "object_var.docx",
        out=tmp_path / "out.docx",
    )


def test_key_and_property_sintaxes_must_work_properly(paths):
    """
    These two ways must work:

    - obj.prop
    - obj["prop"]
    """

    @dataclass
    class Person:
        name: str
        age: int

    person = Person(name=faker.name(), age=faker.random_int(18, 90))
    context = {"person": person}

    tplx = TemplaterX(paths.template)
    tplx.render(context)

    xml = docx.get_rendered_xml(tplx, paths.out)

    name = f"The name is {person.name}"
    age = f"The age is {person.age}"

    assert xml.count(name) == 2
    assert xml.count(age) == 2
