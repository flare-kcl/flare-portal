from django.test import TestCase
from django.utils import timezone

from freezegun import freeze_time

from flare_portal.users.factories import UserFactory

from ..factories import ExperimentFactory, ProjectFactory


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
