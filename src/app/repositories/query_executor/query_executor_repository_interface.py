from src.domain.generic_query_result_model import GenericQueryResultModel
from abc import ABC, abstractmethod


class QueryExecutorRepositoryInterface(ABC):
    @abstractmethod
    def execute(self, name: str, query: str, conn_string: str) -> GenericQueryResultModel:
        raise NotImplementedError()
