import zipfile
import re
import shutil
import os

# Arquivos de entrada e saída
orig_file = "ATA_CORREICAO_WEB.docx.odt"
copy_file = "ATA_CORREICAO_WEB_COPIA.odt"
temp_content = "content_temp.xml"

# Criar uma cópia do ODT original
shutil.copy(orig_file, copy_file)

# Extrair o content.xml
with zipfile.ZipFile(copy_file, "r") as files:
    content = files.read("content.xml").decode()

# Dados a serem inseridos
data = [
    {
        "inicio": "2024-01-01",
        "fim": "2024-12-31",
        "egestao_inicio": "2025-12-24",
        "egestao_fim": "2026-05-01",
        "vara": "1ª Vara Federal de São Paulo",
    },
    {
        "inicio": "2027-05-15",
        "fim": "2028-10-30",
        "egestao_inicio": "2021-01-01",
        "egestao_fim": "2022-12-31",
        "vara": "2ª Vara Federal de São Paulo",
    }
]

# Encontrar a tabela
t1_match = list(re.finditer(
    r"<table:table.*?DADOS_CORREICAO.*?</table:table>", content))[0]
row_match = list(re.finditer(
    r"(<table:table-row.*?</table:table-row>)", t1_match.group()))[-2]

# Criar as novas linhas
row_template = row_match.group()
rows = ""
for d in data:
    row = row_template
    for k, v in d.items():
        var = "{{" + f" d.{k} " + "}}"
        row = row.replace(var, v)
    rows += row

# Inserir as novas linhas no XML
ini, end = row_match.span()
t1 = t1_match.group()[:ini] + rows + t1_match.group()[end:]

ini, end = t1_match.span()
content = content[:ini] + t1 + content[end:]

# Salvar o novo content.xml temporariamente
with open(temp_content, "w", encoding="utf-8") as temp_file:
    temp_file.write(content)

# Criar um novo ODT sem o antigo content.xml
with zipfile.ZipFile(copy_file, "r") as zip_read:
    with zipfile.ZipFile("temp.odt", "w", zipfile.ZIP_DEFLATED) as zip_write:
        for item in zip_read.infolist():
            if item.filename != "content.xml":  # Ignorar o content.xml antigo
                zip_write.writestr(item.filename, zip_read.read(item.filename))


# Substituir o arquivo original pelo modificado
os.replace("temp.odt", copy_file)

# Adicionar o novo content.xml ao ODT
with zipfile.ZipFile(copy_file, "a") as zip_mod:
    with open(temp_content, "rb") as temp_file:
        zip_mod.writestr("content.xml", temp_file.read())

# Remover o arquivo temporário
os.remove(temp_content)

print(f"Arquivo modificado salvo como: {copy_file}")
