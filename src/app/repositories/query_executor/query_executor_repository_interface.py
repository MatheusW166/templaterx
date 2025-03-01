from abc import ABC, abstractmethod
from typing import Any


class QueryExecutorRepositoryInterface(ABC):
    @abstractmethod
    def execute(self, query: str, conn_string: str) -> list[Any]:
        raise NotImplementedError
