from src.app.handlers.message_handler_interface import MessageHandlerInterface

# TODO: Implement message broker handler


class RabbitMQHandler(MessageHandlerInterface):
    def consume(self):
        return super().consume()

    def publish(self):
        return super().publish()
