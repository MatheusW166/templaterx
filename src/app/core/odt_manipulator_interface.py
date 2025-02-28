from abc import ABC, abstractmethod
from src.app.core.xml_processor_interface import XMLProcessorInterface


class OdtManipulatorInterface(ABC):
    @abstractmethod
    def load_contentxml(self, orig_file: str) -> XMLProcessorInterface:
        pass

    @abstractmethod
    def create_no_content_copy(self, orig_file: str, generated_file: str):
        pass

    @abstractmethod
    def generate_document(self, content_xml: str):
        pass
