"""
This benchmark compares two rendering models:

- docxtpl: monolithic rendering, requiring the full context to be loaded
  into memory before rendering.

- templaterx: incremental rendering, allowing large collections to be
  rendered in isolation, reducing peak memory usage.

The goal is to measure peak Python memory usage imposed by each model.
"""

import shutil
import tracemalloc
import uuid
from contextlib import contextmanager
from pathlib import Path
from tempfile import mkdtemp

from docxtpl import DocxTemplate
from faker import Faker

from templaterx import TemplaterX

faker = Faker()
faker.seed_instance(42)

TEMPLATE = Path(__file__).parent / "templates" / "mem_benchmark_tpl.docx"
UUID_NAMESPACE = uuid.UUID("12345678-1234-5678-1234-567812345678")
TMP_PATH = Path(mkdtemp())


def generate_people(n: int) -> list[dict]:
    return [
        {
            "id": uuid.uuid5(UUID_NAMESPACE, str(i)),
            "name": faker.name(),
            "born_at": faker.date_of_birth(minimum_age=18, maximum_age=100),
            "country": faker.country(),
        }
        for i in range(n)
    ]


@contextmanager
def peak_memory(name: str):
    tracemalloc.start()
    yield
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"{name} [Peak]: {peak / 1024**2:.2f} MB")


def run_docxtpl(lists_number: int, list_size: int):
    tpl = DocxTemplate(TEMPLATE)

    context = {}
    for i in range(lists_number):
        context[f"large_list{i + 1}"] = generate_people(list_size)

    tpl.render(context)
    tpl.save(TMP_PATH / "tpl.docx")


def run_templaterx(lists_number: int, list_size: int):
    tplx = TemplaterX(TEMPLATE)

    for i in range(lists_number):
        tplx.render({f"large_list{i + 1}": generate_people(list_size)})

    tplx.save(TMP_PATH / "tplx.docx")


def run():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--list-size", default=10_000, type=int)
    parser.add_argument("--lists-number", default=5, type=int)
    args = parser.parse_args()

    ln, ls = args.lists_number, args.list_size

    # with peak_memory("docxtpl"):
    #     run_docxtpl(lists_number=ln, list_size=ls)

    with peak_memory("templaterx"):
        run_templaterx(lists_number=ln, list_size=ls)

    shutil.rmtree(TMP_PATH)


if __name__ == "__main__":
    run()
