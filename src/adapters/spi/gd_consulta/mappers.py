from src.domain.gd_consulta_model import GDConsultaModel
from src.app.mappers.db_mapper_interface import DbMapperInterface
from src.adapters.spi.gd_consulta.gd_consulta_db_model import GdConsultaDbModel


class GdConsultaDbModelMapper(DbMapperInterface):
    def to_db(self, model: GDConsultaModel) -> GdConsultaDbModel:
        return None

    def to_model(self, dbModel: GdConsultaDbModel) -> GDConsultaModel:
        return GDConsultaModel(
            name=dbModel.nm_consulta,
            description=dbModel.ds_consulta,
            query=dbModel.ds_sql,
            is_active=dbModel.in_ativo,
            created_at=dbModel.dt_criacao,
            is_updated=dbModel.fl_atualizado,
        )
