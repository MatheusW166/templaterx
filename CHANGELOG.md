## [1.0.0] – 2026-XX-XX
🎉 First stable release

This release marks the first stable version of TemplaterX.
The public API is now considered stable and suitable for production use.

### Features

- Incremental rendering for DOCX templates, avoiding full context load upfront
- Full compatibility with docxtpl templates and syntax
- Seamless integration with Jinja2
- Support for RichText, images, tables, and advanced formatting

### Compatibility & Testing

- All original docxtpl tests were replicated and adapted to pytest
- Tests were executed using the same templates provided by the docxtpl author
- Ensures that existing docxtpl templates continue to work correctly with incremental rendering

### Breaking Changes

- None


## 0.1.0
### Initial release
- Incremental and stateful rendering support.
