from jinja2 import Environment, Undefined, meta


class KeepPlaceholderUndefined(Undefined):
    def __str__(self):
        return f"{{{{ {self._undefined_name} }}}}"

    def __getattr__(self, name):
        return f"{{{{ {self._undefined_name}.{name} }}}}"

    def __getitem__(self, key):
        return f"{{{{ {self._undefined_name}['{key}'] }}}}"


def get_environment():
    return Environment(
        undefined=KeepPlaceholderUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def extract_jinja_vars_from_xml(xml: str):
    parsed = Environment().parse(xml)
    return set(meta.find_undeclared_variables(parsed))
