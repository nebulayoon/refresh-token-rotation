import uuid

from sqlalchemy import UUID, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum("USER", "ADMIN", name="role_type"), nullable=False
    )
