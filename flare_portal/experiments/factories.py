from typing import Any, Dict

from django.utils import timezone

import factory
from factory import post_generation

from flare_portal.users.factories import UserFactory

from .models import (
    AffectiveRatingModule,
    BreakEndModule,
    BreakStartModule,
    CriterionModule,
    CriterionQuestion,
    Experiment,
    FearConditioningData,
    FearConditioningModule,
    Participant,
    Project,
    WebModule,
)


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
    trial_length = 10.0
    rating_delay = 1.0
    iti_min_delay = 1
    iti_max_delay = 3


class ParticipantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Participant

    participant_id = factory.Sequence(lambda n: f"participant{n}")
    experiment = factory.SubFactory(ExperimentFactory)


class FearConditioningModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FearConditioningModule

    experiment = factory.SubFactory(ExperimentFactory)
    phase = factory.Faker(
        "random_element", elements=dict(FearConditioningModule.PHASES).keys()
    )
    trials_per_stimulus = factory.Faker("random_int", min=12, max=24)
    reinforcement_rate = factory.Faker("random_int", min=1, max=12)


class FearConditioningDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FearConditioningData

    participant = factory.SubFactory(ParticipantFactory)
    module = factory.SubFactory(FearConditioningModuleFactory)
    trial = factory.Sequence(lambda n: n)
    trial_by_stimulus = factory.Sequence(lambda n: n)
    rating = factory.Sequence(lambda n: n % 9 + 1)
    stimulus = factory.Faker("random_element", elements=["CSA", "CSB"])
    unconditional_stimulus = factory.Faker("random_element", elements=[True, False])
    trial_started_at = factory.LazyFunction(lambda: timezone.now())
    response_recorded_at = factory.LazyFunction(lambda: timezone.now())
    volume_level = factory.Faker("pydecimal", left_digits=1, right_digits=2)
    calibrated_volume_level = factory.Faker("pydecimal", left_digits=1, right_digits=2)
    headphones = factory.Faker("random_element", elements=[True, False])


class CriterionModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CriterionModule

    experiment = factory.SubFactory(ExperimentFactory)
    intro_text = factory.Faker("paragraph")


class CriterionQuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CriterionQuestion

    question_text = factory.Faker("sentence")
    help_text = factory.Faker("paragraph")
    correct_answer = factory.Faker("random_element", elements=[True, False])

    module = factory.SubFactory(CriterionModuleFactory)


class WebModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WebModule

    url = "http://google.com"
    intro_text = factory.Faker("sentence")
    help_text = factory.Faker("paragraph")
    append_participant_id = True


class AffectiveRatingModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AffectiveRatingModule


class BreakStartModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BreakStartModule

    duration = factory.Faker("random_int", min=60, max=600)
    start_title = factory.Faker("sentence")
    end_title = factory.Faker("sentence")

    @post_generation
    def end_module(
        obj: BreakStartModule,
        create: bool,
        extracted: BreakEndModule,
        **kwargs: Dict[str, Any],
    ) -> None:
        if extracted:
            if create:
                extracted.save()

            return

        if create:
            BreakEndModuleFactory.create(
                start_module=obj,
                experiment=obj.experiment,
                **kwargs,
            )
        else:
            obj.end_module = BreakEndModuleFactory.build(
                start_module=obj,
                experiment=obj.experiment,
                **kwargs,
            )


class BreakEndModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BreakEndModule

    start_module = factory.SubFactory(BreakStartModuleFactory)
