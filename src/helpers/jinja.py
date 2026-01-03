from jinja2 import Environment, Undefined, meta
from typing import Optional
from functools import wraps


class KeepPlaceholderUndefined(Undefined):
    def __init__(self, *args, name=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._expr = name or self._undefined_name

    def __str__(self):
        return f"{{{{ {self._expr} }}}}"

    def with_filter(self, filter_expr: str):
        return KeepPlaceholderUndefined(name=f"{self._expr} | {filter_expr}")

    def __getattr__(self, name):
        return f"{{{{ {self._undefined_name}.{name} }}}}"

    def __getitem__(self, key):
        return f"{{{{ {self._undefined_name}['{key}'] }}}}"


def apply_preserve_placeholder_to_all_filters(env: Environment):
    """
    Automatically applies the preserve_placeholder decorator
    to all filters registered in the environment.
    """

    for name, func in list(env.filters.items()):

        if not callable(func):
            continue

        if getattr(func, "_preserve_placeholder_wrapped", False):
            continue

        def make_wrapper(f, filter_name):
            @wraps(f)
            def wrapper(value, *args, **kwargs):
                if isinstance(value, Undefined):
                    if hasattr(value, "with_filter"):
                        args_repr = ", ".join(repr(a) for a in args)
                        kwargs_repr = ", ".join(
                            f"{k}={repr(v)}" for k, v in kwargs.items()
                        )

                        params = ", ".join(
                            p for p in (args_repr, kwargs_repr) if p
                        )

                        filter_expr = (
                            f"{filter_name}({params})" if params else filter_name
                        )

                        return value.with_filter(filter_expr)

                    return value

                return f(value, *args, **kwargs)

            wrapper._preserve_placeholder_wrapped = True  # type: ignore
            return wrapper

        env.filters[name] = make_wrapper(func, name)


def get_keep_placeholders_environment(jinja_env: Optional[Environment] = None):
    env = jinja_env or Environment()
    env.undefined = KeepPlaceholderUndefined
    apply_preserve_placeholder_to_all_filters(env)
    return env


def extract_jinja_vars_from_xml(xml: str, jinja_env: Optional[Environment] = None):
    env = jinja_env or Environment()
    parsed = env.parse(xml)
    return set(meta.find_undeclared_variables(parsed))
