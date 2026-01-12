from jinja2 import Environment, Undefined, meta
from functools import wraps


class KeepPlaceholderUndefined(Undefined):
    def __init__(self, *args, name=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._expr = name or self._undefined_name

    def _render(self):
        return f"{{{{ {self._expr} }}}}"

    def __html__(self):
        return self._render()

    def __str__(self):
        return self._render()

    def __getattr__(self, name):
        expr = f"({self._expr})" if "|" in str(self._expr) else self._expr
        placeholder = f"{expr}.{name}"
        return KeepPlaceholderUndefined(name=placeholder)

    def __getitem__(self, key):
        expr = f"({self._expr})" if "|" in str(self._expr) else self._expr
        placeholder = f"{expr}['{key}']"
        return KeepPlaceholderUndefined(name=placeholder)

    def with_filter(self, filter_expr: str):
        return KeepPlaceholderUndefined(name=f"{self._expr} | {filter_expr}")


def apply_preserve_placeholder_to_all_filters(env: Environment):
    """
    Automatically applies the preserve_placeholder decorator
    to all filters registered in the environment.
    """

    EXCLUDED_JINJA_FILTERS = {"default"}

    for name, func in list(env.filters.items()):
        if name in EXCLUDED_JINJA_FILTERS:
            continue

        if not callable(func):
            continue

        if getattr(func, "_preserve_placeholder_wrapped", False):
            continue

        def make_wrapper(f, filter_name):

            @wraps(f)
            def wrapper(value, *args, **kwargs):
                if not isinstance(value, Undefined):
                    return f(value, *args, **kwargs)

                if isinstance(value, KeepPlaceholderUndefined):
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

            setattr(wrapper, "_preserve_placeholder_wrapped", True)
            return wrapper

        env.filters[name] = make_wrapper(func, name)


def get_keep_placeholders_environment(jinja_env: Environment | None = None, autoescape=False):
    env = jinja_env or Environment()
    env.undefined = KeepPlaceholderUndefined
    env.autoescape = autoescape
    apply_preserve_placeholder_to_all_filters(env)
    return env


def extract_jinja_vars_from_xml(xml: str, jinja_env: Environment | None = None):
    env = jinja_env or Environment()
    parsed = env.parse(xml)
    return set(meta.find_undeclared_variables(parsed))
