from dataclasses import dataclass


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

    def __str__(self):
        return self.clob
