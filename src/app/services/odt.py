import zipfile
from xml_content_processor import ContentXMLProcessor

orig_file = "template.odt"
generated_file = "_generated_doc.odt"


def load_contentxml() -> ContentXMLProcessor:
    with zipfile.ZipFile(orig_file, "r") as files:
        return ContentXMLProcessor(files.read("content.xml"))


def create_no_content_copy(orig_file: str, generated_file: str):
    with zipfile.ZipFile(orig_file, "r") as zip_read:
        with zipfile.ZipFile(generated_file, "w", zipfile.ZIP_DEFLATED) as zip_write:
            for item in zip_read.infolist():
                if item.filename != "content.xml":  # Ignorar o content.xml antigo
                    zip_write.writestr(
                        item.filename, zip_read.read(item.filename))


def generate_document(content_xml: str):
    # Criar novo arquivo .odt
    create_no_content_copy(orig_file, generated_file)

    # Adicionar conteúdo modificado
    with zipfile.ZipFile(generated_file, "a") as zip_mod:
        zip_mod.writestr("content.xml", content_xml)

    print(f"Arquivo modificado salvo como: {generated_file}")
