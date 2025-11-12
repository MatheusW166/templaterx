from abc import ABC, abstractmethod
from typing import Generic, TypeVar

Model = TypeVar("Model")
DbModel = TypeVar("DbModel")


class DbDynamicMapperInterface(ABC, Generic[Model, DbModel]):
    @abstractmethod
    def to_db(self, model: Model) -> DbModel:
        raise NotImplementedError()

    @abstractmethod
    def to_model(self, *args, **kwargs) -> Model:
        raise NotImplementedError()
