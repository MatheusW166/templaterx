from src.domain.base_model import BaseModel
from datetime import datetime
from dataclasses import dataclass


@dataclass
class GDConsultaModel(BaseModel):
    name: str
    description: str
    query: str
    is_active: bool
    created_at: datetime
    is_updated: str
