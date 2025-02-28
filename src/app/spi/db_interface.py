from abc import ABC, abstractmethod


class DbConnectionInterface(ABC):
    @abstractmethod
    def get_connection(self):
        raise NotImplementedError()
