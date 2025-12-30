# TemplaterX

**TemplaterX** is a Python library for **stateful and incremental document rendering**, built on top of **docxtpl**.

Unlike traditional template rendering engines that require the full context upfront, TemplaterX allows you to **render documents progressively**, applying partial contexts over multiple render calls while preserving unresolved placeholders and control blocks.

This approach significantly reduces memory usage and enables streaming or staged data processing.

---

## Key Concept

> **Render documents incrementally, only when data is available.**

TemplaterX maintains an internal template state and allows the `render()` method to be called multiple times.  
Each call applies only the data that can be safely rendered at that moment.

Unresolved placeholders and control blocks remain intact until all required variables are present.

---

## Features

- **Incremental Rendering**
  - Call `render()` multiple times with partial contexts.
  - No need to provide the full context upfront.

- **Lower Memory Usage**
  - Avoids building large in-memory contexts.
  - Ideal for large documents and streamed data sources.

- **Control Block Safety**
  - Control blocks delimited with `{% ... %}` are rendered **only when all internal variables are available**.
  - Otherwise, all its placeholders are preserved.

- **docxtpl based**
  - Uses standard docxtpl syntax.
  - Fully compatible with existing `.docx` templates.

---

## Installation

```bash
pip install templaterx
```

---

## Basic Usage

```python
from templaterx import TemplaterX

tpl = TemplaterX("template.docx")

tpl.render({"name": "John Doe"})
tpl.render({"role": "Some role"})
tpl.render({"salary": 10000})

tpl.save("output.docx")
```

---

## ⚠️ Control Block Rule

A control block is rendered only if all variables used inside it are present in the context. 

If any required variable is missing, placeholders remain unchanged.

---

## Use Cases

- Large document generation

- Streaming data pipelines

- Reports built from multiple data sources

- Memory-constrained environments

- Staged or conditional document assembly