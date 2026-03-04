from database import Base
from sqlalchemy import String

from sqlalchemy.orm import mapped_column, Mapped, relationship


class Users(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(20))

    students = relationship("Students", back_populates="user")
