from src.domain.generic_query_result_model import GenericQueryResultModel
from src.app.mappers.db_dynamic_mapper_interface import DbDynamicMapperInterface
from typing import Any
from sqlalchemy.engine.result import Result


class GenericQueryResultMapper(DbDynamicMapperInterface):
    def to_db(self, model):
        pass

    def to_model(self, result: Result[Any], name: str):
        keys = tuple(result.keys())
        all = result.all()

        return GenericQueryResultModel(
            result=[keys, *all],
            name=name
        )
