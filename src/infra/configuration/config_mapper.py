from src.domain.configuration_model import ConfigurationModel
from typing import Dict, Optional
from dotenv import dotenv_values


class ConfigurationMapper:
    @classmethod
    def get_config(cls, env) -> ConfigurationModel:
        env = env.lower()

        __config_raw: Dict[str, Optional[str]] = dotenv_values(
            ".env.{}".format(env)
        )

        main_datasource_url = __config_raw.get("MAIN_DATASOURCE_URL")
        pool_size = __config_raw.get("POOL_SIZE")

        if main_datasource_url is None or pool_size is None:
            raise RuntimeError(f"Missing {env} configuration")

        return ConfigurationModel(
            main_datasource_url=main_datasource_url,
            pool_size=int(pool_size),
            env=env
        )
