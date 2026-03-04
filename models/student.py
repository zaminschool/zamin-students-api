from database import Base
from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped


class Students(Base):
    __tablename__ = 'students'
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    mark: Mapped[int] = mapped_column()
