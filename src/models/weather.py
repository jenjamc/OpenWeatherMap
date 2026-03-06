from sqlalchemy import Column
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy.orm import Mapped

from src.models.base import BaseModel


class Weather(BaseModel):
    __tablename__ = 'weathers'
    __table_args__ = (
        Index(
            'ix_weathers_created_city_days',
            'created_at',
            'city',
            'hours_forecast',
        ),
    )

    city: Mapped[str] = Column(String, nullable=False, index=True)
    file_path: Mapped[str]
    hours_forecast: Mapped[int]
