import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from sqlalchemy import text
from src.app.spi.db_dynamic_interface import DbDynamicConnectionInterface
from src.adapters.errors.db_error import DBError


class DbDynamicConnection(DbDynamicConnectionInterface):
    def __init__(self, pool_size: int):
        self.engines: list[_sql.Engine] = []
        self.pool_size = pool_size

    def _get_host(self, conn_string: str):
        return conn_string.split("@")[-1]

    def _get_engine_by_url(self, conn_string: str):
        for engine in self.engines:
            if engine.url.host in self._get_host(conn_string.strip()):
                return engine
        return None

    def _add_engine(self, conn_string: str):
        engine = self._get_engine_by_url(conn_string)

        if engine is None:
            engine = _sql.create_engine(
                conn_string,
                pool_size=self.pool_size,
                max_overflow=0
            )
            self.engines.append(engine)

            from src.infra.shared.logs import Logger
            Logger.get_logger().info(f"Connected to database: {engine.url}")

        return engine

    def execute(self, query: str, conn_string: str):
        try:
            engine = self._add_engine(conn_string)
            with _orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )() as conn:
                return conn.execute(text(query))
        except Exception as e:
            raise DBError(e)
