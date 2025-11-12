import zipfile
from src.app.core.odt_manipulator_interface import OdtManipulatorInterface
from src.infra.shared.logs import Logger

DEFAULT_ODT_CONTENT_XML = "content.xml"

logs = Logger.get_logger()


class OdtManipulator(OdtManipulatorInterface):
    def __init__(self, orig_file: str, generated_file: str):
        self.orig_file = orig_file
        self.generated_file = generated_file

    def load_contentxml(self) -> bytes:
        with zipfile.ZipFile(self.orig_file, "r") as files:
            return files.read(DEFAULT_ODT_CONTENT_XML)

    def create_no_content_copy(self):
        with zipfile.ZipFile(self.orig_file, "r") as zip_read:
            with zipfile.ZipFile(self.generated_file, "w", zipfile.ZIP_DEFLATED) as zip_write:
                for item in zip_read.infolist():
                    if item.filename != DEFAULT_ODT_CONTENT_XML:  # Ignores old content.xml
                        zip_write.writestr(
                            item.filename, zip_read.read(item.filename))

    def generate_document(self, content_xml: str):
        # Creates new odt
        self.create_no_content_copy()

        # Adds modified content.xml
        with zipfile.ZipFile(self.generated_file, "a") as zip_mod:
            zip_mod.writestr(
                DEFAULT_ODT_CONTENT_XML,
                content_xml
            )

        logs.info(f"Modified odt saved as: {self.generated_file}")
