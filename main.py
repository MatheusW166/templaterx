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
from src.domain.gd_consulta_model import GDConsultaModel

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

log = Logger.get_logger()


async def exec_query_async(query: GDConsultaModel):
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(
            None,
            query_executor_repository.execute,
            query.name,
            query.query,
            config.main_datasource_url
        )
        log.info(f"✅ Executed query: {query.name}")

        async with asyncio.Lock():
            processor.build_tables_with_name(result.name, result.result)

    except RuntimeError as e:
        log.error(f"Error on {query.name}: {e}")
        pass
    except Exception as e:
        log.error(f"Error on {query.name}: {e.__cause__}")
        pass


async def main():

    await asyncio.gather(*[exec_query_async(c) for c in consultas])

    odt.generate_document(processor.tostring())


asyncio.run(main())
