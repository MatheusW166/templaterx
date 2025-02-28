from abc import ABC, abstractmethod
from typing import Generic, TypeVar

Model = TypeVar("Model")
DbModel = TypeVar("DbModel")


class DbMapperInterface(ABC, Generic[Model, DbModel]):
    @abstractmethod
    def to_db(self, entity: Model) -> DbModel:
        raise NotImplementedError()

    @abstractmethod
    def to_model(self, model: DbModel) -> Model:
        raise NotImplementedError()
