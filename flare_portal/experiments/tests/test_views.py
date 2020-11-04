from django.test import TestCase
from django.urls import reverse

from flare_portal.users.factories import UserFactory

from ..factories import ProjectFactory
from ..models import Project


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


class ProjectCreateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("ADMIN")
        self.user.save()
        self.client.force_login(self.user)

    def test_create_user(self) -> None:
        url = reverse("experiments:project_create")

        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code)

        form_data = {
            "name": "My project",
            "description": "This is my project",
            "owner": str(self.user.pk),
        }

        resp = self.client.post(url, form_data, follow=True)

        project = Project.objects.get()

        self.assertRedirects(
            resp,
            reverse("experiments:experiment_list", kwargs={"project_pk": project.pk}),
        )

        self.assertEqual(project.name, form_data["name"])
        self.assertEqual(project.description, form_data["description"])
        self.assertTrue(project.owner, int(form_data["owner"]))

        self.assertEqual(
            str(list(resp.context["messages"])[0]), f'Added new project "{project}"'
        )


class ProjectUpdateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("ADMIN")
        self.user.save()
        self.client.force_login(self.user)

    def test_update_user(self) -> None:
        project: Project = ProjectFactory()

        url = reverse("experiments:project_update", kwargs={"project_pk": project.pk})

        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code)

        form_data = {
            "name": "My project",
            "description": "This is my project",
            "owner": str(self.user.pk),
        }

        resp = self.client.post(url, form_data, follow=True)

        self.assertRedirects(
            resp,
            reverse("experiments:experiment_list", kwargs={"project_pk": project.pk}),
        )

        project.refresh_from_db()

        self.assertEqual(project.name, form_data["name"])
        self.assertEqual(project.description, form_data["description"])
        self.assertTrue(project.owner, int(form_data["owner"]))

        self.assertEqual(
            str(list(resp.context["messages"])[0]), f'Updated project "{project}"'
        )


class ProjectDeleteViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("ADMIN")
        self.user.save()
        self.client.force_login(self.user)

    def test_delete_user(self) -> None:
        project: Project = ProjectFactory()

        url = reverse("experiments:project_delete", kwargs={"project_pk": project.pk})
        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code)

        resp = self.client.post(url, follow=True)

        self.assertRedirects(resp, reverse("experiments:project_list"))

        self.assertEqual(0, Project.objects.all().count())

        self.assertEqual(
            str(list(resp.context["messages"])[0]), f'Deleted project "{project}"'
        )
