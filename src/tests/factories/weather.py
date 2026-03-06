import factory

from src.models import Weather
from src.tests.factories.base import BaseFactory


class WeatherFactory(BaseFactory):
    class Meta:
        model = Weather
        sqlalchemy_session_persistence = 'commit'

    city = factory.Faker('pystr')
    file_path = factory.Faker('pystr')
    hours_forecast = factory.Faker('pyint')
