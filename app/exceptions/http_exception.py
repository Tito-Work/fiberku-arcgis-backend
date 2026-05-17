from fastapi import HTTPException


class AppException(Exception):
    def __init__(
        self,
        status_code: int = 400,
        code: str = "500",
        message: str = "Error",
        data=None
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.data = data