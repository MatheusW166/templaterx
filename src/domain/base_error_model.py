from src.domain.base_model import BaseModel


class BaseErrorModel(RuntimeError, BaseModel):
    def __init__(self, message, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.message = message
