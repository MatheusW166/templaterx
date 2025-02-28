from dataclasses import dataclass


@dataclass
class ConfigurationModel:
    main_datasource_url: str
    pool_size: int
    env: str
