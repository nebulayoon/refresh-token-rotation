from abc import ABC


class CustomException(ABC, Exception):
    status_code: int
    message: str

    def __init__(
        self,
        status_code: int | None = None,
        message: str | None = None,
    ):
        self.status_code = status_code or self.status_code
        self.message = message or self.message
