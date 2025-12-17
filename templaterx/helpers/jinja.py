from jinja2 import Environment, Undefined, meta
from typing import Optional


class KeepPlaceholderUndefined(Undefined):
    """
    Keep non control blocks variables if they are not in context during rendering.
    """

    def __str__(self):
        return f"{{{{ {self._undefined_name} }}}}"

    def __getattr__(self, name):
        return f"{{{{ {self._undefined_name}.{name} }}}}"

    def __getitem__(self, key):
        return f"{{{{ {self._undefined_name}['{key}'] }}}}"


def get_keep_placeholders_environment(jinja_env: Optional[Environment] = None):
    env = jinja_env or Environment()
    env.undefined = KeepPlaceholderUndefined
    return env


def extract_jinja_vars_from_xml(xml: str):
    parsed = Environment().parse(xml)
    return set(meta.find_undeclared_variables(parsed))
