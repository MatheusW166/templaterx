from dataclasses import dataclass, field
from typing import Literal, Optional


@dataclass
class Structure():
    clob = ""
    is_control_block = False
    is_rendered = False

    def __add__(self, other: str):
        if isinstance(other, str):
            self.clob += other
            return self
        raise TypeError("Unsupported operand type for +")

    def __radd__(self, other: str):
        return self.__add__(other)

    def __str__(self) -> str:
        return self.clob


@dataclass
class DocxComponents():
    """
    Abstract representation of the main components of a DOCX file.
    """

    body: list[Structure] = field(default_factory=list)
    footnotes: list[Structure] = field(default_factory=list)
    properties: dict[str, list[Structure]] = field(default_factory=dict)
    headers: dict[str, list[Structure]] = field(default_factory=dict)
    footers: dict[str, list[Structure]] = field(default_factory=dict)

    Keys = Literal["body", "headers", "footers", "properties", "footnotes"]

    def _get_structures(self, component: Keys, relKey: Optional[str] = None):
        structures = getattr(self, component)
        if isinstance(structures, dict):
            structures = structures.get(relKey, [])
        return structures

    def to_clob(self, component: Keys, relKey: Optional[str] = None):
        structures = self._get_structures(component, relKey)
        return "".join([s.clob for s in structures])

    def is_component_rendered(self, component: Keys, relKey: Optional[str] = None):
        structures = self._get_structures(component, relKey)
        return all([s.is_rendered for s in structures])
