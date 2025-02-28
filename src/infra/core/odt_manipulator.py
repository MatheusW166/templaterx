import zipfile
from src.app.core.odt_manipulator_interface import OdtManipulatorInterface
from src.infra.core.content_xml_processor import ContentXMLProcessor

orig_file = "template.odt"
generated_file = "_generated_doc.odt"


class OdtManipulator(OdtManipulatorInterface):
    def load_contentxml(self, orig_file):
        with zipfile.ZipFile(orig_file, "r") as files:
            return ContentXMLProcessor(files.read("content.xml"))

    def create_no_content_copy(self, orig_file: str, generated_file: str):
        with zipfile.ZipFile(orig_file, "r") as zip_read:
            with zipfile.ZipFile(generated_file, "w", zipfile.ZIP_DEFLATED) as zip_write:
                for item in zip_read.infolist():
                    if item.filename != "content.xml":  # Ignores old content.xml
                        zip_write.writestr(
                            item.filename, zip_read.read(item.filename))

    def generate_document(self, content_xml: str):
        # Creates new odt
        self.create_no_content_copy(orig_file, generated_file)

        # Adds modified content.xml
        with zipfile.ZipFile(generated_file, "a") as zip_mod:
            zip_mod.writestr("content.xml", content_xml)

        print(f"Modified odt save as: {generated_file}")
