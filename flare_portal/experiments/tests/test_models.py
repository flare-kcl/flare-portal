from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from freezegun import freeze_time

from flare_portal.users.factories import UserFactory

from ..factories import (
    ExperimentFactory,
    FearConditioningModuleFactory,
    ParticipantFactory,
    ProjectFactory,
)
from ..models import (
    Experiment,
    FearConditioningData,
    FearConditioningModule,
    Participant,
)


class ProjectTest(TestCase):
    def test_model(self) -> None:
        now = timezone.now()
        user = UserFactory()
        with freeze_time(now):
            project = ProjectFactory(
                name="My project", description="My project description", owner=user
            )

        self.assertEqual(project.name, "My project")
        self.assertEqual(project.description, "My project description")
        self.assertEqual(project.owner, user)

        self.assertEqual(project.created_at, now)
        self.assertEqual(project.updated_at, now)


class ExperimentTest(TestCase):
    def test_model(self) -> None:
        now = timezone.now()

        user = UserFactory()
        project = ProjectFactory()
        with freeze_time(now):
            experiment = ExperimentFactory(
                name="My experiment",
                description="My experiment description",
                code="ABC123",
                owner=user,
                project=project,
            )

        self.assertEqual(experiment.name, "My experiment")
        self.assertEqual(experiment.description, "My experiment description")
        self.assertEqual(experiment.code, "ABC123")
        self.assertEqual(experiment.owner, user)
        self.assertEqual(experiment.project, project)

        self.assertEqual(experiment.created_at, now)
        self.assertEqual(experiment.updated_at, now)

    def test_add_modules(self) -> None:
        experiment: Experiment = ExperimentFactory()
        module: FearConditioningModule = FearConditioningModuleFactory()

        experiment.modules.add(module)

        self.assertEqual(
            experiment.modules.select_subclasses().first(), module  # type: ignore
        )


class ParticipantTest(TestCase):
    def test_model(self) -> None:
        participant: Participant = ParticipantFactory(participant_id="Flare.ABCDEF")

        self.assertEqual(participant.participant_id, "Flare.ABCDEF")


class FearConditioningModuleTest(TestCase):
    def test_display_names(self) -> None:
        module: FearConditioningModule = FearConditioningModuleFactory()

        self.assertEqual("fear conditioning", module.get_module_name())
        self.assertEqual("FEAR_CONDITIONING", module.get_module_tag())
        self.assertEqual("fear-conditioning", module.get_module_slug())
        self.assertEqual("fear_conditioning", module.get_module_snake_case())
        self.assertEqual("FearConditioning", module.get_module_camel_case())

    def test_validation(self) -> None:
        module: FearConditioningModule = FearConditioningModuleFactory.build(
            trials_per_stimulus=12, reinforcement_rate=13
        )

        with self.assertRaises(ValidationError) as e:
            module.clean()

        self.assertIn("reinforcement_rate", e.exception.error_dict)


class FearConditioningDataTest(TestCase):
    def test_model(self) -> None:
        participant: Participant = ParticipantFactory()
        module: FearConditioningModule = FearConditioningModuleFactory()

        FearConditioningData.objects.create(
            participant=participant,
            module=module,
            trial=1,
            rating=5,
            conditional_stimulus="A",
            unconditional_stimulus=True,
            trial_started_at=timezone.now(),
            response_recorded_at=timezone.now(),
            volume_level=78,
            headphones=True,
        )

    def test_detail_values(self) -> None:
        participant: Participant = ParticipantFactory()
        module: FearConditioningModule = FearConditioningModuleFactory()

        data = FearConditioningData.objects.create(
            participant=participant,
            module=module,
            trial=1,
            rating=5,
            conditional_stimulus="A",
            unconditional_stimulus=True,
            trial_started_at=timezone.now(),
            response_recorded_at=timezone.now(),
            volume_level=78,
            headphones=True,
        )

        self.assertEqual(
            data.get_data_values(),
            [
                ("phase", module.get_phase_display()),
                ("trial", data.trial),
                ("rating", data.rating),
                ("CS", data.conditional_stimulus),
                ("US", data.unconditional_stimulus),
                ("trial started at", data.trial_started_at),
                ("response recorded at", data.response_recorded_at),
                ("volume level", data.volume_level),
                ("headphones", data.headphones),
            ],
        )
