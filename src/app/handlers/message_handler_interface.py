from abc import ABC, abstractmethod

# TODO: Define return type


class MessageHandlerInterface(ABC):
    @abstractmethod
    def listenToQueue(self):
        pass
