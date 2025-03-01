import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from src.app.spi.db_interface import DbConnectionInterface
from src.domain.configuration_model import ConfigurationModel


# Must be a singleton


class DbConnection(DbConnectionInterface):
    def __init__(self, config: ConfigurationModel):
        self.conn_string = config.main_datasource_url
        self.pool_size = config.pool_size
        self.engine = _sql.create_engine(
            config.main_datasource_url,
            pool_size=config.pool_size,
            max_overflow=0
        )
        self.SessionLocal = _orm.sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def get_session(self):
        from src.infra.shared.logs import Logger

        Logger.get_logger().info(f"Connected to database: {self.engine.url}")
        return self.SessionLocal
