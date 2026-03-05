import factory

from src.models import Tenant
from src.models import User
from src.tests.factories.base import BaseFactory


class TenantFactory(BaseFactory):
    class Meta:
        model = Tenant
        sqlalchemy_session_persistence = 'commit'


    agent_name = factory.Faker('pystr')
    agent_id = factory.Faker('pystr')
