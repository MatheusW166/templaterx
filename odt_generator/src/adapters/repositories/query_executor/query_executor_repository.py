from src.domain.generic_query_result_model import GenericQueryResultModel
from src.app.repositories.query_executor.query_executor_repository_interface import QueryExecutorRepositoryInterface
from src.adapters.spi.query_executor.db_dynamic_connection import DbDynamicConnection
from src.adapters.spi.query_executor.mappers import GenericQueryResultMapper


class QueryExecutorRepository(QueryExecutorRepositoryInterface):
    def __init__(self, db_connection: DbDynamicConnection):
        self.db_connection = db_connection
        self.mapper = GenericQueryResultMapper()

    def execute(self, name: str, query: str, conn_string: str) -> GenericQueryResultModel:
        result = self.db_connection.execute(
            query,
            conn_string
        )

        return self.mapper.to_model(result, name=name)
