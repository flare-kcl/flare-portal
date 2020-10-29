from django.contrib.auth import get_user_model

import factory

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "user%d" % n)
    first_name = factory.LazyAttribute(lambda o: o.username)
    last_name = "user"
    email = factory.LazyAttribute(lambda o: "%s@example.com" % o.username)

    @factory.post_generation
    def passwd(self, create: bool, extracted: bool, **kwargs: dict) -> None:
        # make the user's password the same as their username
        self.set_password(self.username)
