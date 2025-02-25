import database as _database
import sqlalchemy as _sql


class GDConsulta(_database.Base):
    __tablename__ = "TB_GD_CONSULTA"

    id_consulta = _sql.Column(_sql.Integer, primary_key=True, index=True)
    nm_consulta = _sql.Column(_sql.String)
    ds_consulta = _sql.Column(_sql.String)
    # id_documento = _sql.Column(_sql.Integer)
    # id_banco_dados = _sql.Column(_sql.Integer)
    ds_sql = _sql.Column(_sql.String)
    in_ativo = _sql.Column(_sql.String)
    dt_criacao = _sql.Column(_sql.DateTime)
    ds_sql_criacao_tabela = _sql.Column(_sql.String)
    fl_atualizado = _sql.Column(_sql.String)
