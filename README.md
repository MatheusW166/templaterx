# 🧩 TemplaterX

A lightweight Python engine for automated document generation. It connects to multiple databases, executes pre-saved SQL queries, and fills `.odt` templates dynamically with the retrieved data.

Whether you need to generate reports, certificates, or data-driven forms, **TemplaterX** bridges your data and your documents with flexibility and ease.

## 🚀 Features

- 🔗 **Multiple Datasource Support**: Connect to Oracle, PostgreSQL, MySQL, and other databases;
- 🧠 **Smart Query Execution**: Runs pre-saved SQL queries mapped to templates;
- 📝 **Dynamic ODT Generation**: Fills OpenDocument Text (.odt) templates with live data;
- ⚙️ **Configurable and Extensible**: Easily adapt templates and queries for different use cases;
- 🧰 **CLI or Script Integration**: Works standalone or embedded in Python applications.

## 🧱 Architecture Overview

TemplaterX uses three main layers:

1. **Datasource Manager**: Stores and manages connection strings for different databases;
2. **Query Engine**: Executes SQL queries associated with templates;
3. **Template Processor**: Reads `.odt` templates and replaces placeholders with query results.
