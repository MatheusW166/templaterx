from src.domain.base_model import BaseModel
from typing import Any, Iterable
from dataclasses import dataclass


@dataclass
class GenericQueryResultModel(BaseModel):
    name: str
    result: dict[str, Iterable[Any]]
