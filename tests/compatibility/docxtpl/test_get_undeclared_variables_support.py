from .constants import TEMPLATES_DIR
from tests.helpers import paths as p
from src.templaterx import TemplaterX
import pytest


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "get_undeclared_variables.docx",
        out=tmp_path / "out.docx",
    )


def test_should_return_all_vars_before_render(paths):
    tplx = TemplaterX(paths.template)
    undeclared = tplx.get_undeclared_template_variables()

    expected_vars = {
        "name",
        "age",
        "email",
        "is_student",
        "has_degree",
        "degree_field",
        "skills",
        "projects",
        "company_name",
        "page_number",
        "generation_date",
        "author",
    }

    assert undeclared == expected_vars


def test_should_find_missing_variables_after_incomplete_rendering(paths):
    tplx = TemplaterX(paths.template)

    context = {
        "name": "John Doe",
        "age": 25,
        "email": "john@example.com",
        "is_student": True,
        "skills": ["Python", "Django"],
        "company_name": "Test Corp",
        "author": "Test Author",
    }

    tplx.render(context)
    undeclared = tplx.get_undeclared_template_variables(context=context)

    expected_missing = {
        "has_degree",
        "degree_field",
        "projects",
        "page_number",
        "generation_date",
    }

    assert undeclared == expected_missing


def test_should_return_empty_after_complete_rendering(paths):
    tplx = TemplaterX(paths.template)

    context = {
        "name": "John Doe",
        "age": 25,
        "email": "john@example.com",
        "is_student": True,
        "has_degree": True,
        "degree_field": "Computer Science",
        "skills": ["Python", "Django", "JavaScript"],
        "projects": [
            {"name": "Project A", "year": 2023,
             "description": "A great project"},
            {"name": "Project B", "year": 2024,
             "description": "Another great project"},
        ],
        "company_name": "Test Corp",
        "page_number": 1,
        "generation_date": "2024-01-15",
        "author": "Test Author",
    }

    tplx.render(context)
    undeclared = tplx.get_undeclared_template_variables(context=context)

    assert len(undeclared) == 0


def test_should_find_all_vars_with_custom_env(paths):
    from jinja2 import Environment

    custom_env = Environment()
    tplx = TemplaterX(paths.template, jinja_env=custom_env)

    undeclared = tplx.get_undeclared_template_variables()

    expected_vars = {
        "name",
        "age",
        "email",
        "is_student",
        "has_degree",
        "degree_field",
        "skills",
        "projects",
        "company_name",
        "page_number",
        "generation_date",
        "author",
    }

    assert undeclared == expected_vars
