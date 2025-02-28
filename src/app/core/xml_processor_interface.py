from abc import ABC, abstractmethod


class XMLProcessorInterface(ABC):
    @abstractmethod
    def find_tables(self) -> list[str]:
        raise NotImplementedError()

    @abstractmethod
    def tostring(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def build_tables_with_name(self, name: str, data: list[dict] = []):
        raise NotImplementedError()
