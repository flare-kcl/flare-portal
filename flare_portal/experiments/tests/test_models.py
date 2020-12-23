from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from freezegun import freeze_time

from flare_portal.users.factories import UserFactory

from ..factories import (
    CriterionModuleFactory,
    CriterionQuestionFactory,
    ExperimentFactory,
    FearConditioningModuleFactory,
    ParticipantFactory,
    ProjectFactory,
)
from ..models import (
    BaseModule,
    CriterionData,
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

    def test_reinforcement_rate_validation(self) -> None:
        module: FearConditioningModule = FearConditioningModuleFactory.build(
            trials_per_stimulus=12, reinforcement_rate=13
        )

        with self.assertRaises(ValidationError) as e:
            module.clean()

        self.assertIn("reinforcement_rate", e.exception.error_dict)

    def test_context_vaildation(self) -> None:
        module: FearConditioningModule = FearConditioningModuleFactory.build(
            context="A"
        )

        with self.assertRaises(ValidationError) as e:
            module.clean()

        self.assertIn("context", e.exception.error_dict)


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
            volume_level=0.78,
            calibrated_volume_level=0.85,
            headphones=True,
        )

    def test_data_values(self) -> None:
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
            volume_level=0.78,
            calibrated_volume_level=0.85,
            headphones=True,
        )

        self.assertEqual(
            data.get_data_values(),
            [
                ("phase", module.get_phase_display()),
                ("trial", data.trial),
                ("rating", data.rating),
                ("CS/GS", data.conditional_stimulus),
                ("US", data.unconditional_stimulus),
                ("trial started at", data.trial_started_at),
                ("response recorded at", data.response_recorded_at),
                ("volume level", data.volume_level),
                ("calibrated volume level", data.calibrated_volume_level),
                ("headphones", data.headphones),
            ],
        )

    def test_list_display_columns(self) -> None:
        columns = FearConditioningData.get_list_display_columns()

        self.assertEqual(
            columns, ["participant", "phase", "trial", "CS/GS", "US", "rating"]
        )

    def test_list_display_values(self) -> None:
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
            volume_level=0.78,
            calibrated_volume_level=0.85,
            headphones=True,
        )

        self.assertEqual(
            data.get_list_display_values(),
            [
                ("participant", data.participant),
                ("phase", module.get_phase_display()),
                ("trial", data.trial),
                ("CS/GS", data.conditional_stimulus),
                ("US", data.unconditional_stimulus),
                ("rating", data.rating),
            ],
        )


class ModuleTest(TestCase):
    def test_required_methods(self) -> None:
        # Check all BaseModule subclasses have the required methods
        for subclass in BaseModule.__subclasses__():
            with self.subTest(subclass.__name__):
                get_module_config = getattr(subclass, "get_module_config", None)

                # Check that subclass has its own implementation
                self.assertNotEqual(
                    BaseModule.get_module_config,
                    get_module_config,
                    "Missing `get_module_config` implementation",
                )


class CriterionDataTest(TestCase):
    def test_model(self) -> None:
        participant: Participant = ParticipantFactory()
        module = CriterionModuleFactory()
        required_question_yes = CriterionQuestionFactory(
            module=module, required_answer=True
        )
        required_question_no = CriterionQuestionFactory(
            module=module, required_answer=False
        )
        required_question_either = CriterionQuestionFactory(
            module=module, required_answer=None
        )
        non_required_question = CriterionQuestionFactory(module=module, required=False)

        data = CriterionData(
            participant=participant,
            module=module,
        )

        # Required question yes
        data.question = required_question_yes
        data.answer = True
        self.assertTrue(data.passed)

        data.answer = False
        self.assertFalse(data.passed)

        # Required question no
        data.question = required_question_no
        data.answer = True
        self.assertFalse(data.passed)

        data.answer = False
        self.assertTrue(data.passed)

        # Required question either
        data.question = required_question_either
        data.answer = True
        self.assertTrue(data.passed)

        data.answer = False
        self.assertTrue(data.passed)

        # Non required question
        data.question = non_required_question
        data.answer = None
        self.assertTrue(data.passed)
