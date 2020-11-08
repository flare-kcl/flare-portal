from django.test import TestCase
from django.urls import reverse

from flare_portal.users.factories import UserFactory
from flare_portal.users.models import User

from ..factories import ExperimentFactory, ProjectFactory
from ..models import Experiment, Project


class ProjectAuthorizationTest(TestCase):
    def test_authorization(self) -> None:
        user: User = UserFactory()
        self.client.force_login(user)

        project: Project = ProjectFactory()

        self.assertEqual(
            302, self.client.get(reverse("experiments:project_list")).status_code
        )
        self.assertEqual(
            302, self.client.get(reverse("experiments:project_create")).status_code
        )
        self.assertEqual(
            302,
            self.client.get(
                reverse("experiments:project_update", kwargs={"project_pk": project.pk})
            ).status_code,
        )
        self.assertEqual(
            302,
            self.client.get(
                reverse("experiments:project_delete", kwargs={"project_pk": project.pk})
            ).status_code,
        )

        user.grant_role("RESEARCHER")
        user.save()

        self.assertEqual(
            200, self.client.get(reverse("experiments:project_list")).status_code
        )
        self.assertEqual(
            200, self.client.get(reverse("experiments:project_create")).status_code
        )
        self.assertEqual(
            200,
            self.client.get(
                reverse("experiments:project_update", kwargs={"project_pk": project.pk})
            ).status_code,
        )
        self.assertEqual(
            200,
            self.client.get(
                reverse("experiments:project_delete", kwargs={"project_pk": project.pk})
            ).status_code,
        )


class ProjectListViewTest(TestCase):
    def setUp(self) -> None:
        self.user: User = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()

        self.client.force_login(self.user)

    def test_get(self) -> None:
        projects = ProjectFactory.create_batch(5, owner=self.user)

        resp = self.client.get(reverse("experiments:project_list"))

        self.assertEqual(200, resp.status_code)

        self.assertEqual(projects, list(resp.context["projects"]))


class ProjectCreateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()
        self.client.force_login(self.user)

    def test_create_project(self) -> None:
        url = reverse("experiments:project_create")

        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code)

        self.assertEqual(resp.context["form"].initial["owner"], self.user.pk)

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
        self.assertEqual(project.owner_id, int(form_data["owner"]))

        self.assertEqual(
            str(list(resp.context["messages"])[0]), f'Added new project "{project}"'
        )


class ProjectUpdateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()
        self.client.force_login(self.user)

    def test_update_project(self) -> None:
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
        self.assertEqual(project.owner_id, int(form_data["owner"]))

        self.assertEqual(
            str(list(resp.context["messages"])[0]), f'Updated project "{project}"'
        )


class ProjectDeleteViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()
        self.client.force_login(self.user)

    def test_delete_project(self) -> None:
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


class ExperimentAuthorizationTest(TestCase):
    def test_authorization(self) -> None:
        user: User = UserFactory()
        self.client.force_login(user)

        project: Project = ProjectFactory()
        experiment: Experiment = ExperimentFactory(project=project)

        self.assertEqual(
            302,
            self.client.get(
                reverse(
                    "experiments:experiment_list", kwargs={"project_pk": project.pk}
                )
            ).status_code,
        )
        self.assertEqual(
            302,
            self.client.get(
                reverse(
                    "experiments:experiment_create", kwargs={"project_pk": project.pk}
                )
            ).status_code,
        )
        self.assertEqual(
            302,
            self.client.get(
                reverse(
                    "experiments:experiment_detail",
                    kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
                )
            ).status_code,
        )
        self.assertEqual(
            302,
            self.client.get(
                reverse(
                    "experiments:experiment_update",
                    kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
                )
            ).status_code,
        )
        self.assertEqual(
            302,
            self.client.get(
                reverse(
                    "experiments:experiment_delete",
                    kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
                )
            ).status_code,
        )

        user.grant_role("RESEARCHER")
        user.save()

        self.assertEqual(
            200,
            self.client.get(
                reverse(
                    "experiments:experiment_list", kwargs={"project_pk": project.pk}
                )
            ).status_code,
        )
        self.assertEqual(
            200,
            self.client.get(
                reverse(
                    "experiments:experiment_create", kwargs={"project_pk": project.pk}
                )
            ).status_code,
        )
        self.assertEqual(
            200,
            self.client.get(
                reverse(
                    "experiments:experiment_detail",
                    kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
                )
            ).status_code,
        )
        self.assertEqual(
            200,
            self.client.get(
                reverse(
                    "experiments:experiment_update",
                    kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
                )
            ).status_code,
        )
        self.assertEqual(
            200,
            self.client.get(
                reverse(
                    "experiments:experiment_delete",
                    kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
                )
            ).status_code,
        )


class ExperimentListViewTest(TestCase):
    def setUp(self) -> None:
        self.user: User = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()

        self.client.force_login(self.user)

    def test_get(self) -> None:
        project = ProjectFactory()
        experiments = ExperimentFactory.create_batch(5, project=project)

        resp = self.client.get(
            reverse("experiments:experiment_list", kwargs={"project_pk": project.pk})
        )

        self.assertEqual(200, resp.status_code)

        self.assertEqual(project, resp.context["project"])
        self.assertEqual(experiments, list(resp.context["experiments"]))


class ExperimentCreateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()
        self.client.force_login(self.user)

        self.project = ProjectFactory()

    def test_create_experiment(self) -> None:
        url = reverse(
            "experiments:experiment_create", kwargs={"project_pk": self.project.pk}
        )

        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(resp.context["project"], self.project)
        self.assertEqual(resp.context["form"].initial["project"], self.project.pk)
        self.assertEqual(resp.context["form"].initial["owner"], self.user.pk)

        form_data = {
            "name": "My experiment",
            "description": "This is my experiment",
            "code": "ABC123",
            "owner": str(self.user.pk),
            "project": str(self.project.pk),
        }

        resp = self.client.post(url, form_data, follow=True)

        experiment = Experiment.objects.get()

        self.assertRedirects(
            resp,
            reverse(
                "experiments:experiment_detail",
                kwargs={"project_pk": self.project.pk, "experiment_pk": experiment.pk},
            ),
        )

        self.assertEqual(experiment.name, form_data["name"])
        self.assertEqual(experiment.description, form_data["description"])
        self.assertEqual(experiment.code, form_data["code"])
        self.assertEqual(experiment.owner_id, int(form_data["owner"]))
        self.assertEqual(experiment.project, self.project)

        self.assertEqual(
            str(list(resp.context["messages"])[0]),
            f'Added new experiment "{experiment}"',
        )


class ExperimentUpdateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()
        self.client.force_login(self.user)

    def test_update_experiment(self) -> None:
        experiment: Experiment = ExperimentFactory()

        url = reverse(
            "experiments:experiment_update",
            kwargs={
                "project_pk": experiment.project_id,
                "experiment_pk": experiment.pk,
            },
        )

        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code)

        form_data = {
            "name": "My experiment",
            "description": "This is my experiment",
            "code": "ABC123",
            "owner": str(self.user.pk),
        }

        resp = self.client.post(url, form_data, follow=True)

        self.assertRedirects(
            resp,
            reverse(
                "experiments:experiment_detail",
                kwargs={
                    "project_pk": experiment.project_id,
                    "experiment_pk": experiment.pk,
                },
            ),
        )

        experiment.refresh_from_db()

        self.assertEqual(experiment.name, form_data["name"])
        self.assertEqual(experiment.description, form_data["description"])
        self.assertEqual(experiment.code, form_data["code"])
        self.assertEqual(experiment.owner_id, int(form_data["owner"]))

        self.assertEqual(
            str(list(resp.context["messages"])[0]),
            f'Updated experiment "{experiment}"',
        )

    def test_should_not_update_project(self) -> None:
        original_project = ProjectFactory()
        other_project = ProjectFactory()
        experiment: Experiment = ExperimentFactory(project=original_project)

        url = reverse(
            "experiments:experiment_update",
            kwargs={
                "project_pk": experiment.project_id,
                "experiment_pk": experiment.pk,
            },
        )

        form_data = {
            "name": "My experiment",
            "description": "This is my experiment",
            "code": "ABC123",
            "owner": str(self.user.pk),
            "project": str(other_project.pk),
        }

        self.client.post(url, form_data, follow=True)

        experiment.refresh_from_db()

        self.assertEqual(experiment.project, original_project)


class ExperimentDeleteViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()
        self.client.force_login(self.user)

    def test_delete_experiment(self) -> None:
        project: Project = ProjectFactory()
        experiment: Experiment = ExperimentFactory(project=project)

        url = reverse(
            "experiments:experiment_delete",
            kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
        )
        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code)

        resp = self.client.post(url, follow=True)

        self.assertRedirects(
            resp,
            reverse("experiments:experiment_list", kwargs={"project_pk": project.pk}),
        )

        self.assertEqual(0, Experiment.objects.all().count())

        self.assertEqual(
            str(list(resp.context["messages"])[0]), f'Deleted experiment "{experiment}"'
        )


class ExperimentDetailViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()
        self.client.force_login(self.user)

    def test_get(self) -> None:
        project: Project = ProjectFactory()
        experiment: Experiment = ExperimentFactory(project=project)
        resp = self.client.get(
            reverse(
                "experiments:experiment_detail",
                kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
            )
        )
        self.assertEqual(200, resp.status_code)


class ModuleCreateViewTest(TestCase):
    def setUp(self) -> None:
        self.user: User = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()

        self.client.force_login(self.user)

        self.experiment: Experiment = ExperimentFactory()
        self.project = self.experiment.project

    def test_create_fear_conditioning_module(self) -> None:
        url = reverse(
            "experiments:modules:fear_conditioning_create",
            kwargs={"project_pk": self.project.pk, "experiment_pk": self.experiment.pk},
        )

        resp = self.client.get(url)

        self.assertEqual(200, resp.status_code)

        form_data = {
            "phase": "habituation",
            "trials_per_stimulus": 12,
            "reinforcement_rate": 12,
            "rating_delay": 1.5,
            "experiment": str(self.experiment.pk),
        }

        resp = self.client.post(url, form_data, follow=True)

        module = self.experiment.modules.select_subclasses().get()  # type: ignore

        self.assertRedirects(
            resp,
            reverse(
                "experiments:experiment_detail",
                kwargs={
                    "project_pk": self.project.pk,
                    "experiment_pk": self.experiment.pk,
                },
            ),
        )

        self.assertEqual(module.phase, form_data["phase"])
        self.assertEqual(module.trials_per_stimulus, form_data["trials_per_stimulus"])
        self.assertEqual(module.reinforcement_rate, form_data["reinforcement_rate"])
        self.assertEqual(module.rating_delay, form_data["rating_delay"])
