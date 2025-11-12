from src.domain.base_model import BaseModel
from dataclasses import dataclass


@dataclass
class ConfigurationModel(BaseModel):
    main_datasource_url: str
    postgres_url: str
    pool_size: int
    env: str
