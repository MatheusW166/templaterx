import os
import asyncio

from src.adapters.spi.gd_consulta.db_connection import DbConnection
from src.adapters.spi.query_executor.db_dynamic_connection import DbDynamicConnection
from src.adapters.repositories.gd_consulta.gd_consulta_repository import GdConsultaRepository
from src.adapters.repositories.query_executor.query_executor_repository import QueryExecutorRepository

from src.infra.configuration.config_mapper import ConfigurationMapper
from src.infra.core.odt_manipulator import OdtManipulator
from src.infra.core.content_xml_processor import ContentXMLProcessor
from src.infra.shared.logs import Logger

from src.domain.configuration_model import ConfigurationModel

env = os.getenv("ENV", "dev")
config: ConfigurationModel = ConfigurationMapper.get_config(env)

main_db_connection = DbConnection(config)
gd_consulta_repository = GdConsultaRepository(main_db_connection)

odt = OdtManipulator(orig_file="template.odt", generated_file="_generated.odt")
xml = odt.load_contentxml()

processor = ContentXMLProcessor(xml)
tables = processor.find_tables()

consultas = gd_consulta_repository.get_all_in_names(tables)

dynamic_db_connection = DbDynamicConnection(config.pool_size)
query_executor_repository = QueryExecutorRepository(dynamic_db_connection)


async def main():
    loop = asyncio.get_running_loop()

    async def one_fetch(c):
        try:
            await loop.run_in_executor(
                None,
                query_executor_repository.execute,
                c.query,
                config.main_datasource_url
            )
            Logger.get_logger().info(
                f"✅ Successfully executed query: {c.name}"
            )
        except Exception as e:
            Logger.get_logger().error(
                f"Error executing query {c.name}: {e.__cause__}")

    coros = [one_fetch(c) for c in consultas]
    await asyncio.gather(*coros)

asyncio.run(main())
