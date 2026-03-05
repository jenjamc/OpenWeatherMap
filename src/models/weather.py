from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import Mapped

from src.models.base import BaseModel


class Weather(BaseModel):
    __tablename__ = 'weathers'

    city: Mapped[str] = Column(String, nullable=False, index=True)
    file_path: Mapped[str]
