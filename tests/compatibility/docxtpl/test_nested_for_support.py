from src.templaterx import TemplaterX
from .constants import TEMPLATES_DIR
from tests.helpers import paths as p, docx
import pytest


@pytest.fixture
def paths(tmp_path):
    return p.Paths(
        template=TEMPLATES_DIR / "nested_for_tpl.docx",
        out=tmp_path / "out.docx",
    )


# -------------------------
# Helpers
# -------------------------

def is_all_dishes_rendered(dishes: list[dict], xml: str):
    return all(
        (
            dishe["name"] in xml and
            all(ingredient in xml for ingredient in dishe["ingredients"])
        )
        for dishe in dishes
    )


def is_any_dishes_rendered(dishes: list[dict], xml: str):
    return any(
        (
            dishe["name"] in xml and
            any(ingredient in xml for ingredient in dishe["ingredients"])
        )
        for dishe in dishes
    )


def is_all_authors_rendered(authors: list[dict], xml: str):
    return all(
        (
            xml.count(author["name"]) == 3 and
            all(
                title in xml
                for title in [book["title"] for book in author["books"]]
            )
        )
        for author in authors
    )


# -------------------------
# Tests
# -------------------------

def test_nested_for_should_be_rendered_properly_with_incremental_rendering_until_complete_context(paths):
    tplx = TemplaterX(paths.template)

    context = {
        "dishes": [
            {
                "name": "Pizza",
                "ingredients": ["bread", "tomato", "ham", "cheese"]
            },
            {
                "name": "Hamburger",
                "ingredients": ["bread", "chopped steak", "cheese", "sauce"],
            },
            {
                "name": "Apple pie",
                "ingredients": ["flour", "apples", "suggar", "quince jelly"],
            },
        ],
    }

    tplx.render(context)

    context["authors"] = [
        {
            "name": "Saint-Exupery",
            "books": [
                    {"title": "Le petit prince"},
                    {"title": "L'aviateur"},
                    {"title": "Vol de nuit"},
            ],
        },
        {
            "name": "Barjavel",
            "books": [
                    {"title": "Ravage"},
                    {"title": "La nuit des temps"},
                    {"title": "Le grand secret"},
            ],
        },
    ]

    tplx.render(context)

    xml = docx.get_rendered_xml(tplx, paths.out)

    dishes = context["dishes"]
    authors = context["authors"]

    assert is_all_dishes_rendered(dishes, xml)
    assert is_all_authors_rendered(authors, xml)


def test_nested_for_should_render_available_data_and_keep_placeholders_with_partial_context(paths):
    tplx = TemplaterX(paths.template)

    context = {
        "dishes": [
            {
                "name": "Pizza",
                "ingredients": ["bread", "tomato", "ham", "cheese"]
            },
            {
                "name": "Hamburger",
                "ingredients": ["bread", "chopped steak", "cheese", "sauce"],
            },
            {
                "name": "Apple pie",
                "ingredients": ["flour", "apples", "suggar", "quince jelly"],
            },
        ],
        # "authors": [...]
    }

    tplx.render(context)
    xml = docx.get_rendered_xml(tplx, paths.out)

    dishes = context["dishes"]

    assert is_all_dishes_rendered(dishes, xml)
    assert r"{% for author in authors %}" in xml
    assert r"{% for book in author.books %}" in xml
    assert r"{{ author.name }}" in xml
    assert r"{{ book.title }}" in xml
    assert r"{% endfor %}" in xml
    assert r"{% endfor %}" in xml


def test_nested_for_should_not_render_when_intern_vars_are_missing(paths):
    """
    When *dishes* is defined but *EXCLUDED_DISHES* is missing, nothing 
    should be rendered for dishes.

    Other control blocks should be rendered as usual.

    #### Template example::

        {%p for  dish  in dishes if  dish.name not in EXCLUDED_DISHES %}
            {{ dish.name }} : {% for ingredient in dish.ingredients %}{{ingredient}}, {% endfor %}
        {%p endfor %}
    """

    tplx = TemplaterX(paths.template)

    context = {
        # "EXCLUDED_DISHES": ["Pizza", "Apple pie"],
        "dishes": [
            {
                "name": "Pizza",
                "ingredients": ["bread", "tomato", "ham", "cheese"]
            },
            {
                "name": "Hamburger",
                "ingredients": ["bread", "chopped steak", "cheese", "sauce"],
            },
            {
                "name": "Apple pie",
                "ingredients": ["flour", "apples", "suggar", "quince jelly"],
            },
        ],
        "authors": [
            {
                "name": "Saint-Exupery",
                "books": [
                    {"title": "Le petit prince"},
                    {"title": "L'aviateur"},
                    {"title": "Vol de nuit"},
                ],
            },
            {
                "name": "Barjavel",
                "books": [
                    {"title": "Ravage"},
                    {"title": "La nuit des temps"},
                    {"title": "Le grand secret"},
                ],
            },
        ]
    }

    tplx.render(context)
    xml = docx.get_rendered_xml(tplx, paths.out).split("Another example")[-1]

    dishes = context["dishes"]
    authors = context["authors"]

    # Authors should be rendered
    assert is_all_authors_rendered(authors, xml)

    # Dishes must have its placeholder kept
    assert not is_any_dishes_rendered(dishes, xml)

    assert r"{% for  dish  in dishes if  dish.name not in EXCLUDED_DISHES %}" in xml
    assert r"{{ dish.name }}" in xml
    assert r"{% for ingredient in dish.ingredients %}" in xml
    assert r"{{ingredient}}" in xml
    assert r"{% endfor %}" in xml
    assert r"{% endfor %}" in xml


def test_nested_for_should_be_rendered_and_processed_normally_when_all_loop_vars_are_defined(paths):

    tplx = TemplaterX(paths.template)

    context = {
        "EXCLUDED_DISHES": ["Pizza"],
        "dishes": [
            {
                "name": "Pizza",
                "ingredients": ["bread", "tomato", "ham", "cheese"]
            },
            {
                "name": "Hamburger",
                "ingredients": ["bread", "chopped steak", "cheese", "sauce"],
            },
            {
                "name": "Apple pie",
                "ingredients": ["flour", "apples", "suggar", "quince jelly"],
            },
        ],

    }

    tplx.render(context)
    xml = docx.get_rendered_xml(tplx, paths.out).split("Another example")[-1]

    dishes = context["dishes"]

    # As we have excluded "Pizza", not all dishes will be rendered
    assert is_any_dishes_rendered(dishes, xml)
    assert not is_all_dishes_rendered(dishes, xml)
