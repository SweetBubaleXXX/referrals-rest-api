from factory import Factory, Faker

from src.features.users.models import User


class UserFactory(Factory):
    email = Faker("email")
    password = Faker("password")

    class Meta:
        model = User
