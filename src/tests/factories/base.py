import factory


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    id = factory.Sequence(lambda n: n)
    created_at = factory.Faker('date_object')
    updated_at = factory.Faker('date_object')
