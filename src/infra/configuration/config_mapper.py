from src.domain.configuration_model import ConfigurationModel
from typing import Dict, Optional
from dotenv import dotenv_values


class ConfigurationMapper:
    @classmethod
    def get_config(cls, env: str) -> ConfigurationModel:
        env = env.lower()

        __config_raw: Dict[str, Optional[str]] = dotenv_values(
            ".env.{}".format(env)
        )

        main_datasource_url = __config_raw.get("MAIN_DATASOURCE_URL")
        postgres_url = __config_raw.get("POSTGRES_URL")
        pool_size = __config_raw.get("POOL_SIZE")

        if None in [main_datasource_url, pool_size, postgres_url]:
            raise RuntimeError(f"Missing '{env}' configuration")

        return ConfigurationModel(
            main_datasource_url=main_datasource_url,
            postgres_url=postgres_url,
            pool_size=int(pool_size),
            env=env
        )
