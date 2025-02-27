import src.domain.models as _models
import src.infra.database as _database
import src.app.services.odt as _odt
from sqlalchemy import text

db = _database.SessionLocal()

xml_content = _odt.load_contentxml()
tables = xml_content.find_tables()

queries = db.query(_models.GDConsulta).where(
    _models.GDConsulta.nm_consulta.in_(tables)).all()

for query in queries:
    print("Executing query:", query.nm_consulta)
    result = db.execute(text(query.ds_sql))
    columns = list(result.keys())

    rows = [list(t) for t in result.all()]
    data = [columns, *rows]

    print("Filling table")
    template_content_xml = xml_content.build_tables_with_name(
        query.nm_consulta,
        data
    )

print("Generating document")
_odt.generate_document(xml_content.tostring())
