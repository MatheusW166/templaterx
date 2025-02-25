import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import sqlalchemy.ext.declarative as _declarative
import os
from dotenv import load_dotenv

load_dotenv(override=True)

engine = _sql.create_engine(os.getenv("MAIN_DATASOURCE_URL"))
SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = _declarative.declarative_base()