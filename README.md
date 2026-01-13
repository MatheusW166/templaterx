![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![uv](https://img.shields.io/badge/uv-%23DE5FE9.svg?style=for-the-badge&logo=uv&logoColor=white) ![Jinja](https://img.shields.io/badge/jinja-white.svg?style=for-the-badge&logo=jinja&logoColor=black)

# TemplaterX


This is a Python library for incremental document rendering, built on top of [docxtpl](https://github.com/elapouya/python-docx-template).

Unlike traditional template rendering engines that require the full context upfront, TemplaterX allows you to render documents progressively, applying partial contexts over multiple render calls.


## Key Concept

> **Render documents incrementally, only when data is available.**

Each call applies only the data that can be safely rendered at that moment. Unresolved placeholders and control blocks remain intact until all required variables are present.


## Features

- **Incremental Rendering**;

- **Lower Memory Usage**:
  - Avoids building large in-memory contexts.
- **Control Block Safety**:
  - Control blocks delimited with `{% ... %}` are rendered **only when all internal variables are available**;
  - Otherwise, all its placeholders are preserved.

- **docxtpl based**:
  - Uses standard docxtpl syntax;
  - Fully compatible with existing `.docx` templates (see [Running Tests](#running-tests) section).


## Installation

```bash
pip install templaterx
```


## Basic Usage

```python
from templaterx import TemplaterX

tplx = TemplaterX("template.docx")

tplx.render({"name": "John Doe"})
tplx.render({"role": "Some role"})
tplx.render({"salary": 10000})

tplx.save("output.docx")
```


## Template Syntax

TemplaterX does not introduce a new template syntax.

All templates follow the same syntax and rules defined by **docxtpl**, which is itself based on **Jinja2**.  

For a detailed reference, please see the following docs:
- [docxtpl](https://docxtpl.readthedocs.io/)
- [Jinja2](https://jinja.palletsprojects.com/en/stable/templates/)


## Control Block Rule

A control block is rendered only if all variables used inside it are present in the context. 

If any required variable is missing, placeholders remain unchanged.


### Incremental vs Monolithic Rendering

Traditional template engines such as docxtpl operate using a monolithic rendering model: the entire context must be fully constructed and loaded into memory before rendering can begin.

This approach works well for small or medium-sized documents, but it introduces significant memory pressure when dealing with:

- **Large collections**;

- **Data coming from multiple sources**;
- **Streaming or paginated datasets**.


## Use Cases

- **Large document generation**;

- **Streaming data pipelines**;
- **Reports built from multiple data sources**;
- **Memory-constrained environments**;
- **Staged or conditional document assembly**.


## Development & Contributing

Contributions, feedback, and experimentation are welcome!

In short, this project is closely tied to understanding how different execution strategies affect memory usage, composability, and data flow.

If you are interested in improving the project, exploring new use cases, or validating its behavior in different environments, the sections below should help you get started.

---
### Running Tests

TemplaterX uses **pytest** for automated testing.
```bash
# To run the full test suite locally
uv run pytest
```
In order to ensure compatibility and feature parity, the test suite was largely derived from the original docxtpl tests, with small adaptations to use pytest and to account for the incremental rendering model.

The tests were executed using **the same .docx templates** provided by the original author of docxtpl.

---
### Benchmarks

#### Disclaimer

Any benchmark comparing docxtpl and TemplaterX should be interpreted as a comparison between rendering models, not as a direct, absolute comparison between libraries.

- docxtpl enforces a monolithic render by design;
- TemplaterX enables an incremental render by design.

Benchmarks that show lower peak memory usage for TemplaterX are demonstrating the impact of incremental rendering, not merely an optimization of the underlying template engine.

The primary design goal of TemplaterX is to enable **progressive rendering as data becomes available**, which is useful when fetching data from external sources such as databases, APIs, or streaming pipelines.

> Lower peak memory usage is a positive and expected consequence of this execution model, rather than its sole motivation.

---
#### Running Memory Benchmark

The project includes a small memory benchmark intended to illustrate architectural differences between rendering strategies.

In a nutshell, we are comparing:

- **A monolithic rendering model**, where the full context must be loaded before rendering;
- **An incremental rendering model**, where data can be rendered progressively as it becomes available.

To run the memory benchmark:
```bash
uv run python -m benchmarks.memory [--lists-number N] [--list-size N]
```
Where:

- **--lists-number**: number of large collections rendered;
- **--list-size**: number of items per collection.
  
Example:
```bash
uv run python -m benchmarks.memory --lists-number 5 --list-size 10000
```

The benchmark reports peak Python memory usage observed during rendering. Results may vary depending on the runtime environment and dataset size, and should be interpreted as a qualitative comparison that highlights trade-offs between execution models.

Benchmarks are exploratory and are primarily meant to support design discussions and informed decision-making.

---
If you have ideas, suggestions, or alternative approaches to incremental document rendering, feel free to open an issue or start a discussion.
