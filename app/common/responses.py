from decimal import Decimal
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, field_validator

T = TypeVar("T")


class ResponseEntity(BaseModel, Generic[T]):
    success: bool = True
    message: Optional[str] = None
    data: T | None = None

    @field_validator("data", mode="before")
    def convert_decimals_to_float(cls, value):
        return cls.__convert(value)

    @classmethod
    def __convert(cls, item: Any) -> Any:
        if isinstance(item, Decimal):
            return float(item)
        elif isinstance(item, list):
            return [cls.__convert(sub_itme) for sub_itme in item]
        elif isinstance(item, dict):
            return {key: cls.__convert(sub_value) for key, sub_value in item.items()}
        return item

    @classmethod
    def create(cls):
        return ResponseEntity[None](success=True, message="Created Successfully")

    @classmethod
    def ok(cls, message="Success"):
        return ResponseEntity[None](success=True, message=message)

    @classmethod
    def ok_with_data(cls):
        return ResponseEntity[T](success=True, message="Items Fetch Successfully")

    @classmethod
    def failed(cls):
        return ResponseEntity[None](success=False, message="Failed")
