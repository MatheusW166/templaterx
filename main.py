import database as _database
import models as _models
import utils as _utils
from sqlalchemy import text

db = _database.SessionLocal()

template_content_xml = _utils.load_contentxml()
tables = _utils.find_tables(template_content_xml)

open("_content.xml", "w").write(template_content_xml)

temp = _utils.fill_table("PRAZOS_MEDIOS_COMPARACAO", template_content_xml,[["ALGO"],[1]])
# _utils.fill_table("PERIODO_PRAZO_TIPO", temp,[["ALGO"],[1]])

open("_temp_content.xml", "w").write(temp)

exit(0)

queries = db.query(_models.GDConsulta).where(_models.GDConsulta.nm_consulta.in_(tables)).all()

for query in queries:
    print("Executing query:", query.nm_consulta)
    result = db.execute(text(query.ds_sql))
    columns = list(result.keys())

    rows = [list(t) for t in result.all()]
    data = [columns, *rows]

    print("Filling table")
    template_content_xml = _utils.fill_table(query.nm_consulta, template_content_xml, data)

print("Generating document")
_utils.generate_document(template_content_xml)