from abc import ABC, abstractmethod


class DbConnectionInterface(ABC):
    @abstractmethod
    def get_session(self):
        raise NotImplementedError()
