"""
This benchmark compares two rendering models:

- docxtpl: monolithic rendering, requiring the full context to be loaded
  into memory before rendering.

- templaterx: incremental rendering, allowing large collections to be
  rendered in isolation, reducing peak memory usage.

The goal is to measure peak Python memory usage imposed by each model.
"""


from pathlib import Path
from contextlib import contextmanager
from faker import Faker
from docxtpl import DocxTemplate
from templaterx import TemplaterX
import tracemalloc
import uuid


faker = Faker()
faker.seed_instance(42)

TEMPLATE = Path(__file__).parent / "templates" / "mem_benchmark_tpl.docx"
UUID_NAMESPACE = uuid.UUID("12345678-1234-5678-1234-567812345678")
PEOPLE_PER_LIST = 10_000
LISTS = 5


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


def run_docxtpl():
    tpl = DocxTemplate(TEMPLATE)

    context = {}
    for i in range(LISTS):
        context[f"large_list{i+1}"] = generate_people(PEOPLE_PER_LIST)

    tpl.render(context)


def run_templaterx():
    tplx = TemplaterX(TEMPLATE)

    for i in range(LISTS):
        tplx.render({
            f"large_list{i+1}": generate_people(PEOPLE_PER_LIST)
        })


def run():
    with peak_memory("docxtpl"):
        run_docxtpl()

    with peak_memory("templaterx"):
        run_templaterx()


if __name__ == "__main__":
    run()
