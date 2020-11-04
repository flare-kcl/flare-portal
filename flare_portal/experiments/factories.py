import factory

from flare_portal.users.factories import UserFactory

from .models import Experiment, Project


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: "project%d" % n)
    description = factory.Faker("paragraph")
    owner = factory.SubFactory(UserFactory)


class ExperimentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Experiment

    name = factory.Sequence(lambda n: "experiment%d" % n)
    description = factory.Faker("paragraph")
    owner = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)
