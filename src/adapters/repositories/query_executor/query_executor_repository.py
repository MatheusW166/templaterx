from src.app.repositories.query_executor.query_executor_repository_interface import QueryExecutorRepositoryInterface
from src.adapters.spi.query_executor.db_dynamic_connection import DbDynamicConnection
from typing import Any


class QueryExecutorRepository(QueryExecutorRepositoryInterface):
    def __init__(self, db_connection: DbDynamicConnection):
        self.db_connection = db_connection

    def execute(self, query: str, conn_string: str) -> list[Any]:
        results = self.db_connection.execute(
            query,
            conn_string
        ).all()
        return results
