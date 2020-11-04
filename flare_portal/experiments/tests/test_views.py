from django.test import TestCase
from django.urls import reverse

from flare_portal.users.factories import UserFactory

from ..factories import ProjectFactory


class ProjectAuthorizationTest(TestCase):
    def test_authorization(self) -> None:
        self.fail()


class ProjectListViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()

        self.client.force_login(self.user)

    def test_get(self) -> None:
        projects = ProjectFactory.create_batch(5, owner=self.user)

        resp = self.client.get(reverse("experiments:project_list"))

        self.assertEqual(200, resp.status_code)

        self.assertEqual(projects, list(resp.context["projects"]))
