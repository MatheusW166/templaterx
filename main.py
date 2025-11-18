# import os
# import asyncio

# from src.adapters.spi.gd_consulta.db_connection import DbConnection
# from src.adapters.spi.query_executor.db_dynamic_connection import DbDynamicConnection
# from src.adapters.repositories.gd_consulta.gd_consulta_repository import GdConsultaRepository
# from src.adapters.repositories.query_executor.query_executor_repository import QueryExecutorRepository

# from src.infra.configuration.config_mapper import ConfigurationMapper
# from src.infra.core.odt_manipulator import OdtManipulator
# from src.infra.core.content_xml_processor import ContentXMLProcessor
# from src.infra.shared.logs import Logger

# from src.domain.configuration_model import ConfigurationModel
# from src.domain.gd_consulta_model import GDConsultaModel

# env = os.getenv("ENV", "dev")
# config: ConfigurationModel = ConfigurationMapper.get_config(env)

# main_db_connection = DbConnection(config)
# gd_consulta_repository = GdConsultaRepository(main_db_connection)

# odt = OdtManipulator(orig_file="template.odt", generated_file="_generated.odt")
# xml = odt.load_contentxml()

# processor = ContentXMLProcessor(xml)
# tables = processor.find_all_vars()

# consultas = gd_consulta_repository.get_all_in_names(tables)

# dynamic_db_connection = DbDynamicConnection(config.pool_size)
# query_executor_repository = QueryExecutorRepository(dynamic_db_connection)

# log = Logger.get_logger()


# async def exec_query_async(query: GDConsultaModel):
#     loop = asyncio.get_running_loop()
#     try:
#         # Executing each operation in a separate thread
#         result = await loop.run_in_executor(
#             None,
#             query_executor_repository.execute,
#             query.name,
#             query.query,
#             config.postgres_url
#         )

#         # Locking to ensure that only one thread can modify the xml at a time
#         async with asyncio.Lock():
#             processor.fill_content(result.name, result.result)
#     except Exception as e:
#         log.error(f"Error on {query.name}: {e}")
#         pass


# async def main():
#     await asyncio.gather(*[exec_query_async(c) for c in consultas])
#     odt.generate_document(processor.tostring())


# if __name__ == "__main__":
#     asyncio.run(main())


import re
from docxtpl import DocxTemplate

# First render
doc = DocxTemplate("template.docx")
doc.render({
    "TABLE": [
        {"a": 1, "b": 4},
        {"c": 3, "d": 7}
    ],
})

# Second render
doc.render({
    "ANOTHER_TABLE": [
        {"a": 5, "b": 7},
        {"c": 5, "d": 5}
    ],
})

doc.save("_generated.docx")

exit(0)


clob = open("doc.xml", "r").read()


def extract_jinja_blocks(xml_content: str):

    # Padrões para detectar início e fim de blocos
    open_pattern = re.compile(r"\{\%\s*(for|if|block)\b.*?\%\}")
    close_pattern = re.compile(r"\{\%\s*end(for|if|block)\s*\%\}")

    # Tokenizar o texto em partes Jinja e não-Jinja
    tokens = re.split(r"(\{\%.*?\%\})", xml_content, flags=re.DOTALL)

    structures = []
    stack = []
    current_block = ""

    for token in tokens:
        if not token.strip():
            continue

        if open_pattern.match(token):
            # início de um bloco
            if not stack:
                current_block = token  # inicia novo bloco
            else:
                current_block += token
            stack.append(token)

        elif close_pattern.match(token):
            # fim de um bloco
            current_block += token
            if stack:
                stack.pop()
            if not stack:
                # bloco completo finalizado
                structures.append(current_block.strip())
                current_block = ""
        else:
            # conteúdo XML ou texto entre os blocos
            if stack:
                current_block += token

    return structures


result = extract_jinja_blocks(clob)

print(result[1])
