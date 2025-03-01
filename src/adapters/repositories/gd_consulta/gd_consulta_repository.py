from src.domain.gd_consulta_model import GDConsultaModel
from src.app.repositories.gd_consulta.gd_consulta_repository_interface import GdConsultaRepositoryInterface
from src.adapters.spi.gd_consulta.db_connection import DbConnection
from src.adapters.spi.gd_consulta.gd_consulta_db_model import GdConsultaDbModel
from src.adapters.spi.gd_consulta.mappers import GdConsultaDbModelMapper


class GdConsultaRepository(GdConsultaRepositoryInterface):
    def __init__(self, db_connection: DbConnection):
        self.db_connection = db_connection
        self.mapper = GdConsultaDbModelMapper()

    def get_all(self) -> list[GDConsultaModel]:
        session = self.db_connection.get_connection()
        results = session.query(GdConsultaDbModel).all()
        return [self.mapper.to_model(result) for result in results]

    def get_all_in_names(self, names: list[str]) -> list[GDConsultaModel]:
        Session = self.db_connection.get_session()

        with Session() as conn:
            results = conn.query(GdConsultaDbModel).filter(GdConsultaDbModel.nm_consulta.in_(names)).all()
            return [self.mapper.to_model(result) for result in results]