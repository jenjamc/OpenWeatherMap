import factory

from src.models import User
from src.tests.factories.base import BaseFactory


class UserFactory(BaseFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = 'commit'

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    password_hash = factory.Faker('pystr')
