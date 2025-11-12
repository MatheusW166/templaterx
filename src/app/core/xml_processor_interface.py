from abc import ABC, abstractmethod


class XMLProcessorInterface(ABC):
    @abstractmethod
    def find_all_vars(self) -> list[str]:
        raise NotImplementedError()

    @abstractmethod
    def tostring(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def fill_content(self, name: str, data: list[dict] = []):
        raise NotImplementedError()
