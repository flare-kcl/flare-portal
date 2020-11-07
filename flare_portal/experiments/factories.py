import factory

from flare_portal.users.factories import UserFactory

from .models import Experiment, FearConditioningModule, Project


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: f"project{n}")
    description = factory.Faker("paragraph")
    owner = factory.SubFactory(UserFactory)


class ExperimentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Experiment

    name = factory.Sequence(lambda n: f"experiment{n}")
    description = factory.Faker("paragraph")
    code = factory.Sequence(lambda n: f"CODE{n:02}")
    owner = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)


class FearConditioningModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FearConditioningModule

    experiment = factory.SubFactory(ExperimentFactory)
