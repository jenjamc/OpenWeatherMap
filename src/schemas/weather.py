from pydantic import BaseModel
from pydantic import Field
from pydantic import RootModel


class WeatherRequestSchema(BaseModel):
    cities: list[str]
    days_forecast: int = Field(default=1, le=5, ge=1)

    @property
    def hours_forecast(self) -> int:
        return self.days_forecast * 8


class WeatherSchema(BaseModel):
    id: int
    main: str
    description: str
    icon: str


class MainWeatherSchema(BaseModel):
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    sea_level: int | None = None
    grnd_level: int | None = None
    humidity: int
    temp_kf: float | None = None


class CloudsSchema(BaseModel):
    all: int


class WindSchema(BaseModel):
    speed: float
    deg: int
    gust: float | None = None


class SysSchema(BaseModel):
    pod: str


class CoordSchema(BaseModel):
    lat: float
    lon: float


class CitySchema(BaseModel):
    id: int
    name: str
    coord: CoordSchema
    country: str
    population: int
    timezone: int
    sunrise: int
    sunset: int


class ForecastItemSchema(BaseModel):
    dt: int
    main: MainWeatherSchema
    weather: list[WeatherSchema]
    clouds: CloudsSchema
    wind: WindSchema
    visibility: int
    pop: float
    sys: SysSchema
    dt_txt: str


class ForecastResponseSchema(BaseModel):
    cod: str
    message: int
    cnt: int
    list: list[ForecastItemSchema]
    city: CitySchema


class WeatherBatchResponseSchema(RootModel[ForecastResponseSchema]):
    pass
