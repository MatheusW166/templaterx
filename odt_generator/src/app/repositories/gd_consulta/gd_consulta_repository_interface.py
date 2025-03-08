from abc import ABC, abstractmethod
from src.domain.gd_consulta_model import GDConsultaModel


class GdConsultaRepositoryInterface(ABC):
    @abstractmethod
    def get_all(self) -> list[GDConsultaModel]:
        raise NotImplementedError()

    @abstractmethod
    def get_all_in_names(self, names: list[str]) -> list[GDConsultaModel]:
        raise NotImplementedError()
