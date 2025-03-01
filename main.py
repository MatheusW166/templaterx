import os

from src.adapters.spi.gd_consulta.db_connection import DbConnection
from src.adapters.repositories.gd_consulta.gd_consulta_repository import GdConsultaRepository
from src.infra.configuration.config_mapper import ConfigurationMapper
from src.domain.configuration_model import ConfigurationModel

env = os.getenv("ENV", "dev")
config: ConfigurationModel = ConfigurationMapper.get_config(env)

main_db_connection = DbConnection(config)
gd_consulta_repository = GdConsultaRepository(main_db_connection)

consultas = gd_consulta_repository.get_all()
print(len(consultas))
