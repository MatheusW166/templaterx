from abc import ABC, abstractmethod

# TODO: Define return type


class MessageHandlerInterface(ABC):
    @abstractmethod
    def consume(self):
        pass

    def publish(self):
        pass
