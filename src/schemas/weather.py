from datetime import datetime
from typing import Any

from pydantic import BaseModel
from pydantic import Field


class WeatherResultSchema(BaseModel):
    city: str = Field(description='Requested city name')
    requested_at: datetime = Field(description='UTC timestamp when the API response was produced')
    cached: bool = Field(description='True if the response came from local 5-minute cache')
    source: str = Field(description='Data source: provider or cache')
    file_path: str = Field(description='Path to the stored JSON payload on disk')
    payload: dict[str, Any] = Field(description='Raw weather payload returned by the provider or cache')


class WeatherErrorSchema(BaseModel):
    city: str
    status_code: int
    message: str


class WeatherResponseSchema(BaseModel):
    forecast_days: int = Field(description='Forecast horizon in days (1 for current weather, 3 for forecast)')
    results: list[WeatherResultSchema]
    errors: list[WeatherErrorSchema] = Field(default_factory=list)
    
    
class WeatherRequestSchema(BaseModel):
    cities: list[str]
    days_forecast: int = Field(default=1, le=40, ge=1)


class WeatherRequestForecastSchema(BaseModel):
    city: str
    days_forecast: int = Field(default=1, le=40, ge=1)
