from src.domain.base_model import BaseModel
from typing import Any
from dataclasses import dataclass


@dataclass
class GenericQueryResultModel(BaseModel):
    name: str
    result: list[tuple[Any]]
