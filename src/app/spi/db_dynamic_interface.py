from abc import ABC, abstractmethod


class DbDynamicConnectionInterface(ABC):
    @abstractmethod
    def execute(self, query: str, conn_string: str):
        raise NotImplementedError()
