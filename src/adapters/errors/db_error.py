from src.app.errors.db_error_interface import DBErrorInterface


class DBError(DBErrorInterface):
    def __init__(self, exception: Exception):
        super().__init__(exception.__cause__, exception)
