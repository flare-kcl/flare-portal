import csv
import io
from typing import Any, Dict, List

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from freezegun import freeze_time
from rest_framework.test import APITestCase

from flare_portal.users.factories import UserFactory
from flare_portal.users.models import User

from ..factories import (
    BreakStartModuleFactory,
    ExperimentFactory,
    FearConditioningDataFactory,
    FearConditioningModuleFactory,
    ParticipantFactory,
    ProjectFactory,
)
from ..models import (
    BaseModule,
    BreakEndModule,
    BreakStartModule,
    CriterionModule,
    Experiment,
    FearConditioningData,
    FearConditioningModule,
    Participant,
    Project,
)

test_file = "flare_portal/experiments/tests/assets/circle.png"


class ProjectAuthorizationTest(TestCase):
    def test_authorization(self) -> None:
        user: User = UserFactory()
        self.client.force_login(user)

        project: Project = ProjectFactory(owner=user)

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

        # print(len(projects))
        # print(len(resp.context["projects"]))

        self.assertCountEqual(projects, list(resp.context["projects"]))


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
        project: Project = ProjectFactory(owner=self.user)

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
        project: Project = ProjectFactory(owner=self.user)

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

        project: Project = ProjectFactory(owner=user)
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
        project = ProjectFactory(owner=self.user)
        experiments = ExperimentFactory.create_batch(5, project=project)

        resp = self.client.get(
            reverse("experiments:experiment_list", kwargs={"project_pk": project.pk})
        )

        self.assertEqual(200, resp.status_code)

        self.assertEqual(project, resp.context["project"])
        self.assertEqual(experiments, list(resp.context["experiments"]))

    def test_get_experiments_only_for_the_current_project(self) -> None:
        project_1 = ProjectFactory(owner=self.user)
        experiments_1 = ExperimentFactory.create_batch(5, project=project_1)
        project_2 = ProjectFactory(owner=self.user)
        ExperimentFactory.create_batch(5, project=project_2)

        resp = self.client.get(
            reverse("experiments:experiment_list", kwargs={"project_pk": project_1.pk})
        )

        self.assertEqual(200, resp.status_code)

        self.assertEqual(project_1, resp.context["project"])
        self.assertEqual(experiments_1, list(resp.context["experiments"]))


class ExperimentCreateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()
        self.client.force_login(self.user)

        self.project = ProjectFactory(owner=self.user)

    def test_create_experiment(self) -> None:
        url = reverse(
            "experiments:experiment_create", kwargs={"project_pk": self.project.pk}
        )

        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(resp.context["project"], self.project)
        self.assertEqual(resp.context["form"].initial["project"], self.project.pk)
        self.assertEqual(resp.context["form"].initial["owner"], self.user.pk)

        # File uploads
        us_file = SimpleUploadedFile(
            "file.wav", b"wav content", content_type="audio/wav"
        )
        csa_file = SimpleUploadedFile(
            "csa.png", open(test_file, "rb").read(), content_type="image/png"
        )
        csb_file = SimpleUploadedFile(
            "csa.png", open(test_file, "rb").read(), content_type="image/png"
        )
        context_a_file = SimpleUploadedFile(
            "context_a.png",
            open(test_file, "rb").read(),
            content_type="image/png",
        )
        context_b_file = SimpleUploadedFile(
            "context_b.png",
            open(test_file, "rb").read(),
            content_type="image/png",
        )
        context_c_file = SimpleUploadedFile(
            "context_c.png",
            open(test_file, "rb").read(),
            content_type="image/png",
        )

        form_data: Dict[str, Any] = {
            "name": "My experiment",
            "description": "This is my experiment",
            "code": "ABC123",
            "owner": str(self.user.pk),
            "project": str(self.project.pk),
            "trial_length": "5.0",
            "rating_delay": "1.5",
            "iti_min_delay": "1",
            "iti_max_delay": "3",
            "minimum_volume": "1",
            "us_file_volume": "0.5",
            "rating_scale_anchor_label_left": "Certain no beep",
            "rating_scale_anchor_label_center": "Uncertain",
            "rating_scale_anchor_label_right": "Certain beep",
            "us": us_file,
            "csa": csa_file,
            "csb": csb_file,
            "context_a": context_a_file,
            "context_b": context_b_file,
            "context_c": context_c_file,
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
        self.assertEqual(experiment.trial_length, float(form_data["trial_length"]))
        self.assertEqual(experiment.rating_delay, float(form_data["rating_delay"]))
        self.assertEqual(experiment.iti_min_delay, int(form_data["iti_min_delay"]))
        self.assertEqual(experiment.iti_max_delay, int(form_data["iti_max_delay"]))

        self.assertEqual(
            experiment.rating_scale_anchor_label_left,
            form_data["rating_scale_anchor_label_left"],
        )
        self.assertEqual(
            experiment.rating_scale_anchor_label_center,
            form_data["rating_scale_anchor_label_center"],
        )
        self.assertEqual(
            experiment.rating_scale_anchor_label_right,
            form_data["rating_scale_anchor_label_right"],
        )

        self.assertEqual(
            str(list(resp.context["messages"])[0]),
            f'Added new experiment "{experiment}"',
        )

        # Files exist
        self.assertTrue(experiment.us)
        self.assertTrue(experiment.csa)
        self.assertTrue(experiment.csb)
        self.assertTrue(experiment.context_a)
        self.assertTrue(experiment.context_b)
        self.assertTrue(experiment.context_c)

    def test_field_validation(self) -> None:
        url = reverse(
            "experiments:experiment_create", kwargs={"project_pk": self.project.pk}
        )

        form_data = {
            "name": "My experiment",
            "description": "This is my experiment",
            "code": "WHAT@1",
            "owner": str(self.user.pk),
            "project": str(self.project.pk),
            "trial_length": "10.0",
            "rating_delay": "15.0",
            "iti_min_delay": "6",
            "iti_max_delay": "3",
        }

        resp = self.client.post(url, form_data, follow=True)

        self.assertEqual(200, resp.status_code)

        self.assertEqual(
            resp.context["form"].errors["code"][0],
            "Please only enter alphanumeric values.",
        )

        self.assertEqual(
            resp.context["form"].errors["rating_delay"][0],
            "Rating delay cannot be longer than the trial length.",
        )

        self.assertEqual(
            resp.context["form"].errors["iti_min_delay"][0],
            "Minimum delay cannot be shorter than maximum delay.",
        )


class ExperimentUpdateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()
        self.client.force_login(self.user)

    def test_update_experiment(self) -> None:
        project = ProjectFactory(owner=self.user)
        experiment: Experiment = ExperimentFactory(project=project)

        url = reverse(
            "experiments:experiment_update",
            kwargs={
                "project_pk": experiment.project_id,
                "experiment_pk": experiment.pk,
            },
        )

        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code)

        # Assets
        us_file = SimpleUploadedFile(
            "file.wav", b"wav content", content_type="audio/wav"
        )
        csa_file = SimpleUploadedFile(
            "csa.png", open(test_file, "rb").read(), content_type="image/png"
        )
        csb_file = SimpleUploadedFile(
            "csa.png", open(test_file, "rb").read(), content_type="image/png"
        )

        form_data: Dict[str, Any] = {
            "name": "My experiment",
            "description": "This is my experiment",
            "code": "ABC123",
            "owner": str(self.user.pk),
            "trial_length": "5.0",
            "rating_delay": "1.5",
            "iti_min_delay": "1",
            "iti_max_delay": "3",
            "minimum_volume": "1",
            "us_file_volume": "0.5",
            "rating_scale_anchor_label_left": "Certain no beep",
            "rating_scale_anchor_label_center": "Uncertain",
            "rating_scale_anchor_label_right": "Certain beep",
            "us": us_file,
            "csa": csa_file,
            "csb": csb_file,
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
        self.assertEqual(experiment.trial_length, float(form_data["trial_length"]))
        self.assertEqual(experiment.rating_delay, float(form_data["rating_delay"]))
        self.assertEqual(experiment.iti_min_delay, int(form_data["iti_min_delay"]))
        self.assertEqual(experiment.iti_max_delay, int(form_data["iti_max_delay"]))
        self.assertEqual(
            experiment.rating_scale_anchor_label_left,
            form_data["rating_scale_anchor_label_left"],
        )
        self.assertEqual(
            experiment.rating_scale_anchor_label_center,
            form_data["rating_scale_anchor_label_center"],
        )
        self.assertEqual(
            experiment.rating_scale_anchor_label_right,
            form_data["rating_scale_anchor_label_right"],
        )

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
        project: Project = ProjectFactory(owner=self.user)
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
        project: Project = ProjectFactory(owner=self.user)
        experiment: Experiment = ExperimentFactory(project=project)
        FearConditioningModuleFactory.create_batch(5, experiment=experiment)
        resp = self.client.get(
            reverse(
                "experiments:experiment_detail",
                kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
            )
        )
        self.assertEqual(200, resp.status_code)

        self.assertEqual(
            list(experiment.modules.select_subclasses()),  # type: ignore
            list(resp.context["modules"]),
        )

    def test_get_modules_only_for_current_experiment(self) -> None:
        project: Project = ProjectFactory(owner=self.user)
        experiment_1: Experiment = ExperimentFactory(project=project)
        modules_1 = FearConditioningModuleFactory.create_batch(
            5, experiment=experiment_1
        )

        experiment_2: Experiment = ExperimentFactory(project=project)
        FearConditioningModuleFactory.create_batch(5, experiment=experiment_2)
        resp = self.client.get(
            reverse(
                "experiments:experiment_detail",
                kwargs={"project_pk": project.pk, "experiment_pk": experiment_1.pk},
            )
        )
        self.assertEqual(200, resp.status_code)

        self.assertEqual(
            modules_1,
            list(resp.context["modules"]),
        )


class ModuleCreateViewTest(TestCase):
    def setUp(self) -> None:
        self.user: User = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()

        self.client.force_login(self.user)

        context_a_file = SimpleUploadedFile(
            "context_a.png",
            open("flare_portal/experiments/tests/assets/circle.png", "rb").read(),
            content_type="image/png",
        )

        self.project = ProjectFactory(owner=self.user)
        self.experiment: Experiment = ExperimentFactory(
            project=self.project, context_a=context_a_file
        )

    def test_create_fear_conditioning_module(self) -> None:
        url = reverse(
            "experiments:modules:fear_conditioning_create",
            kwargs={"project_pk": self.project.pk, "experiment_pk": self.experiment.pk},
        )

        resp = self.client.get(url)

        self.assertEqual(200, resp.status_code)

        self.assertEqual(FearConditioningModule, resp.context["module_type"])
        self.assertEqual(self.experiment.pk, resp.context["form"].initial["experiment"])

        form_data = {
            "phase": "habituation",
            "trials_per_stimulus": 12,
            "reinforcement_rate": 12,
            "generalisation_stimuli_enabled": True,
            "experiment": str(self.experiment.pk),
            "context": "A",
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
        self.assertEqual(
            module.generalisation_stimuli_enabled,
            form_data["generalisation_stimuli_enabled"],
        )
        self.assertEqual(module.context, "A")

        self.assertEqual(
            str(list(resp.context["messages"])[0]),
            "Added Fear Conditioning module",
        )

    def test_create_criterion_module(self) -> None:
        # Criterion module should have a formset for the questions
        url = reverse(
            "experiments:modules:criterion_create",
            kwargs={"project_pk": self.project.pk, "experiment_pk": self.experiment.pk},
        )

        resp = self.client.get(url)

        self.assertEqual(200, resp.status_code)

        self.assertEqual(CriterionModule, resp.context["module_type"])
        self.assertEqual(self.experiment.pk, resp.context["form"].initial["experiment"])

        form_data = {
            "intro_text": "Intro 123",
            "experiment": str(self.experiment.pk),
            "questions-TOTAL_FORMS": "3",
            "questions-INITIAL_FORMS": "0",
            "questions-MIN_NUM_FORMS": "0",
            "questions-MAX_NUM_FORMS": "1000",
            "questions-0-id": "",
            "questions-0-question_text": "This is question 1",
            "questions-0-help_text": "This is help text 1",
            "questions-0-correct_answer": True,
            "questions-0-sortorder": "1",
            "questions-0-DELETE": "",
            "questions-1-id": "",
            "questions-1-question_text": "This is question 2",
            "questions-1-help_text": "This is help text 2",
            "questions-1-correct_answer": False,
            "questions-1-sortorder": "2",
            "questions-1-DELETE": "",
            "questions-2-id": "",
            "questions-2-question_text": "This is question 3",
            "questions-2-help_text": "This is help text 3",
            "questions-2-correct_answer": False,
            "questions-2-sortorder": "3",
            "questions-2-DELETE": "",
        }

        resp = self.client.post(url, form_data, follow=True)

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

        # Verify data

        module: CriterionModule = (
            self.experiment.modules.select_subclasses().get()  # type: ignore
        )

        self.assertEqual(module.intro_text, form_data["intro_text"])

        questions = module.questions.all()

        self.assertEqual(questions[0].question_text, "This is question 1")
        self.assertEqual(questions[0].help_text, "This is help text 1")
        self.assertEqual(questions[0].correct_answer, True)
        self.assertEqual(questions[0].sortorder, 1)

        self.assertEqual(questions[1].question_text, "This is question 2")
        self.assertEqual(questions[1].help_text, "This is help text 2")
        self.assertEqual(questions[1].correct_answer, False)
        self.assertEqual(questions[1].sortorder, 2)

        self.assertEqual(questions[2].question_text, "This is question 3")
        self.assertEqual(questions[2].help_text, "This is help text 3")
        self.assertEqual(questions[2].correct_answer, False)
        self.assertEqual(questions[2].sortorder, 3)

        self.assertEqual(
            str(list(resp.context["messages"])[0]),
            "Added Criterion module",
        )

    def test_create_break_module(self) -> None:
        existing_module = FearConditioningModuleFactory(experiment=self.experiment)

        url = reverse(
            "experiments:modules:break_start_create",
            kwargs={"project_pk": self.project.pk, "experiment_pk": self.experiment.pk},
        )

        resp = self.client.get(url)

        self.assertEqual(200, resp.status_code)

        self.assertEqual(BreakStartModule, resp.context["module_type"])
        self.assertEqual(self.experiment.pk, resp.context["form"].initial["experiment"])

        form_data = {
            "experiment": str(self.experiment.pk),
            "duration": "300",
            "start_title": "This is the start title,",
            "start_body": "This is the start body,",
            "end_title": "This is the end title,",
            "end_body": "This is the end body,",
        }

        resp = self.client.post(url, form_data, follow=True)

        modules = self.experiment.modules.select_subclasses().all()  # type: ignore

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

        start_module = modules[0]
        end_module = modules[1]

        # Check ordering
        self.assertIsInstance(start_module, BreakStartModule)
        self.assertIsInstance(end_module, BreakEndModule)
        self.assertEqual(existing_module, modules[2])

        self.assertEqual(start_module.duration, int(form_data["duration"]))
        self.assertEqual(start_module.start_title, form_data["start_title"])
        self.assertEqual(start_module.start_body, form_data["start_body"])
        self.assertEqual(start_module.end_title, form_data["end_title"])
        self.assertEqual(start_module.end_body, form_data["end_body"])

        # Should create end break module
        self.assertEqual(start_module.end_module, end_module)

        self.assertEqual(
            str(list(resp.context["messages"])[0]),
            "Added Break module",
        )

    def test_update_ordering(self) -> None:
        # When a new module is created, it is added as the first module in the
        # list. All the other modules are shifted down in the order
        existing_modules = FearConditioningModuleFactory.create_batch(
            5,
            experiment=self.experiment,
        )

        for index, module in enumerate(existing_modules):
            module.sortorder = index
            module.save()

        url = reverse(
            "experiments:modules:fear_conditioning_create",
            kwargs={"project_pk": self.project.pk, "experiment_pk": self.experiment.pk},
        )

        form_data = {
            "phase": "habituation",
            # factory doesn't make modules with 42 trials per stimulus
            "trials_per_stimulus": 42,
            "reinforcement_rate": 12,
            "generalisation_stimuli_enabled": True,
            "experiment": str(self.experiment.pk),
            "context": "A",
        }

        resp = self.client.post(url, form_data, follow=True)

        self.assertEqual(6, len(resp.context["modules"]))

        # Existing modules should have shifted down
        self.assertEqual(resp.context["modules"][0].trials_per_stimulus, 42)
        self.assertEqual(resp.context["modules"][1], existing_modules[0])
        self.assertEqual(resp.context["modules"][2], existing_modules[1])
        self.assertEqual(resp.context["modules"][3], existing_modules[2])
        self.assertEqual(resp.context["modules"][4], existing_modules[3])
        self.assertEqual(resp.context["modules"][5], existing_modules[4])


class ModuleUpdateViewTest(TestCase):
    def setUp(self) -> None:
        self.user: User = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()

        self.client.force_login(self.user)

        self.project = ProjectFactory(owner=self.user)
        self.experiment: Experiment = ExperimentFactory(project=self.project)

    def test_update_fear_conditioning_module(self) -> None:
        module: FearConditioningModule = FearConditioningModuleFactory(
            experiment=self.experiment
        )

        url = reverse(
            "experiments:modules:fear_conditioning_update",
            kwargs={
                "project_pk": self.project.pk,
                "experiment_pk": self.experiment.pk,
                "module_pk": module.pk,
            },
        )

        resp = self.client.get(url)

        self.assertEqual(200, resp.status_code)
        self.assertEqual(type(module), resp.context["module_type"])

        form_data = {
            "phase": "habituation",
            "trials_per_stimulus": 12,
            "reinforcement_rate": 12,
            "generalisation_stimuli_enabled": True,
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
        self.assertEqual(
            module.generalisation_stimuli_enabled,
            form_data["generalisation_stimuli_enabled"],
        )

        self.assertEqual(
            str(list(resp.context["messages"])[0]),
            "Updated Fear Conditioning module",
        )


class ModuleDeleteViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()
        self.client.force_login(self.user)

    def test_delete_fear_conditioning_module(self) -> None:
        project: Project = ProjectFactory(owner=self.user)
        experiment: Experiment = ExperimentFactory(project=project)
        module: FearConditioningModule = FearConditioningModuleFactory(
            experiment=experiment
        )

        url = reverse(
            "experiments:modules:fear_conditioning_delete",
            kwargs={
                "project_pk": project.pk,
                "experiment_pk": experiment.pk,
                "module_pk": module.pk,
            },
        )
        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code)

        resp = self.client.post(url, follow=True)

        self.assertRedirects(
            resp,
            reverse(
                "experiments:experiment_detail",
                kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
            ),
        )

        self.assertEqual(0, BaseModule.objects.all().count())

        self.assertEqual(
            str(list(resp.context["messages"])[0]),
            "Deleted Fear Conditioning module",
        )


class ParticipantCreateBatchViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()
        self.client.force_login(self.user)

    def test_create_batch(self) -> None:
        project: Project = ProjectFactory(owner=self.user)
        experiment: Experiment = ExperimentFactory(project=project)
        url = reverse(
            "experiments:participant_create_batch",
            kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
        )

        resp = self.client.get(url)

        self.assertEqual(200, resp.status_code)
        self.assertEqual(resp.context["experiment"], experiment)

        form_data = {
            "participant_count": "42",
        }

        resp = self.client.post(url, form_data)

        self.assertRedirects(
            resp,
            reverse(
                "experiments:participant_list",
                kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
            ),
        )

        participants = Participant.objects.all()

        self.assertEqual(int(form_data["participant_count"]), len(participants))

        for participant in participants:
            with self.subTest(participant=participant):
                experiment_code, participant_code = participant.participant_id.split(
                    "."
                )
                self.assertEqual(experiment_code, experiment.code)
                self.assertEqual(6, len(participant_code))


class ParticipantUploadViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()
        self.client.force_login(self.user)

    def test_upload(self) -> None:
        project: Project = ProjectFactory(owner=self.user)
        experiment: Experiment = ExperimentFactory(project=project)
        url = reverse(
            "experiments:participant_upload",
            kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
        )

        # Check form view loads
        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(resp.context["experiment"], experiment)

        # Get the CSV import template
        csv_file = open("flare_portal/static_src/misc/participant-template.csv", "rb")
        template = SimpleUploadedFile(
            "participant-template.csv", csv_file.read(), content_type="text/csv"
        )
        form_data = {"import_file": template}

        # Submit upload form
        resp = self.client.post(url, form_data)

        # Check it redirects successfully
        self.assertRedirects(
            resp,
            reverse(
                "experiments:participant_list",
                kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
            ),
        )

        # Check each Participant in the file has been created
        participants = Participant.objects.all()
        data = io.StringIO(csv_file.read().decode("utf-8"))
        for pid in csv.DictReader(data):
            self.assertEqual(participants.filter(participant_id=pid).exists(), True)


class ParticipantFormSetViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()
        self.client.force_login(self.user)

    def test_update_participants(self) -> None:
        project: Project = ProjectFactory(owner=self.user)
        experiment: Experiment = ExperimentFactory(project=project)
        participants: List[Participant] = ParticipantFactory.create_batch(
            3, experiment=experiment
        )
        url = reverse(
            "experiments:participant_list",
            kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
        )

        resp = self.client.get(url)

        self.assertEqual(200, resp.status_code)
        self.assertEqual(resp.context["experiment"], experiment)

        form_data = {
            "participants-TOTAL_FORMS": "6",
            "participants-INITIAL_FORMS": "3",
            "participants-MIN_NUM_FORMS": "0",
            "participants-MAX_NUM_FORMS": "1000",
            "participants-0-id": str(participants[0].pk),
            "participants-0-experiment": str(experiment.pk),
            "participants-0-participant_id": participants[0].participant_id,
            "participants-0-DELETE": "",
            "participants-1-id": str(participants[1].pk),
            "participants-1-experiment": str(experiment.pk),
            "participants-1-participant_id": participants[1].participant_id,
            "participants-1-DELETE": "on",
            "participants-2-id": str(participants[2].pk),
            "participants-2-experiment": str(experiment.pk),
            "participants-2-participant_id": "change",
            "participants-2-DELETE": "",
            "participants-3-id": "",
            "participants-3-experiment": str(experiment.pk),
            "participants-3-participant_id": "new",
            "participants-3-DELETE": "",
            "participants-4-id": "",
            "participants-4-experiment": str(experiment.pk),
            "participants-4-participant_id": "",
            "participants-4-DELETE": "",
            "participants-5-id": "",
            "participants-5-experiment": str(experiment.pk),
            "participants-5-participant_id": "",
            "participants-5-DELETE": "",
        }

        resp = self.client.post(url, form_data, follow=True)

        self.assertRedirects(resp, url)

        result = experiment.participants.all()

        self.assertEqual(3, len(result))
        self.assertEqual(result[0].participant_id, participants[0].participant_id)
        self.assertEqual(result[1].participant_id, "change")
        self.assertEqual(result[2].participant_id, "new")

        self.assertEqual(
            str(list(resp.context["messages"])[0]),
            "Added 1 new participant. Changed 1 participant. Deleted 1 participant.",
        )


class DataListViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()
        self.client.force_login(self.user)

    def test_get(self) -> None:
        project: Project = ProjectFactory(owner=self.user)
        experiment: Experiment = ExperimentFactory(project=project)
        module: FearConditioningModule = FearConditioningModuleFactory(
            experiment=experiment
        )
        data: List[FearConditioningData] = FearConditioningDataFactory.create_batch(
            10, module=module
        )
        url = reverse(
            "experiments:data:fear_conditioning_data_list",
            kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
        )

        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)

        self.assertEqual(resp.context["data_type"], FearConditioningData)
        self.assertEqual(list(resp.context["data"]), data)

    def test_filter(self) -> None:
        # Can filter by participant
        project: Project = ProjectFactory(owner=self.user)
        experiment: Experiment = ExperimentFactory(project=project)
        module: FearConditioningModule = FearConditioningModuleFactory(
            experiment=experiment
        )
        FearConditioningDataFactory.create_batch(10, module=module)

        # Data for a single participant
        participant: Participant = ParticipantFactory(experiment=experiment)
        participant_data: List[
            FearConditioningData
        ] = FearConditioningDataFactory.create_batch(
            10, module=module, participant=participant
        )
        url = reverse(
            "experiments:data:fear_conditioning_data_list",
            kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
        )

        resp = self.client.get(url, {"participant": participant.participant_id})

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(participant, resp.context["participant"])
        self.assertEqual(list(resp.context["data"]), participant_data)

    def test_data_list_view_override(self) -> None:
        # Should be able to override the pregenerated DataListView
        project: Project = ProjectFactory(owner=self.user)
        experiment: Experiment = ExperimentFactory(project=project)
        module_1: FearConditioningModule = FearConditioningModuleFactory(
            experiment=experiment,
            sortorder=2,
        )
        module_2: FearConditioningModule = FearConditioningModuleFactory(
            experiment=experiment,
            sortorder=1,
        )
        participant_1: Participant = ParticipantFactory(experiment=experiment)
        participant_2: Participant = ParticipantFactory(experiment=experiment)
        data = sorted(
            [
                FearConditioningDataFactory(
                    trial=4, module=module_1, participant=participant_1
                ),
                FearConditioningDataFactory(
                    trial=2, module=module_1, participant=participant_1
                ),
                FearConditioningDataFactory(
                    trial=3, module=module_1, participant=participant_1
                ),
                FearConditioningDataFactory(
                    trial=1, module=module_1, participant=participant_1
                ),
                FearConditioningDataFactory(
                    trial=4, module=module_2, participant=participant_2
                ),
                FearConditioningDataFactory(
                    trial=2, module=module_2, participant=participant_2
                ),
                FearConditioningDataFactory(
                    trial=3, module=module_2, participant=participant_2
                ),
                FearConditioningDataFactory(
                    trial=1, module=module_2, participant=participant_2
                ),
                FearConditioningDataFactory(
                    trial=4, module=module_1, participant=participant_2
                ),
                FearConditioningDataFactory(
                    trial=2, module=module_1, participant=participant_2
                ),
                FearConditioningDataFactory(
                    trial=3, module=module_1, participant=participant_2
                ),
                FearConditioningDataFactory(
                    trial=1, module=module_1, participant=participant_2
                ),
            ],
            key=lambda d: (d.participant_id, d.module.sortorder, d.trial),
        )
        url = reverse(
            "experiments:data:fear_conditioning_data_list",
            kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
        )

        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)

        self.assertEqual(resp.context["data_type"], FearConditioningData)
        self.assertEqual(list(resp.context["data"]), data)


class DataDetailViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()
        self.client.force_login(self.user)

    def test_get(self) -> None:
        project: Project = ProjectFactory(owner=self.user)
        experiment: Experiment = ExperimentFactory(project=project)
        module: FearConditioningModule = FearConditioningModuleFactory(
            experiment=experiment
        )
        data: FearConditioningData = FearConditioningDataFactory(module=module)

        url = reverse(
            "experiments:data:fear_conditioning_data_detail",
            kwargs={
                "project_pk": project.pk,
                "experiment_pk": experiment.pk,
                "data_pk": data.pk,
            },
        )

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(resp.context["data_type"], FearConditioningData)
        self.assertEqual(resp.context["data"], data)


class ModuleSortViewTest(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()
        self.client.force_login(self.user)

    def test_sort_modules(self) -> None:
        project: Project = ProjectFactory(owner=self.user)
        experiment: Experiment = ExperimentFactory(project=project)
        modules = FearConditioningModuleFactory.create_batch(5, experiment=experiment)

        # Reverse the sorting
        json_data = {
            modules[0].pk: 5,
            modules[1].pk: 4,
            modules[2].pk: 3,
            modules[3].pk: 2,
            modules[4].pk: 1,
        }

        url = reverse(
            "experiments:module_sort",
            kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
        )

        resp = self.client.post(url, json_data, format="json")

        self.assertEqual(200, resp.status_code)

        self.assertEqual(resp.json()["message"], "Saved ordering.")

        sorted_modules = experiment.modules.order_by("sortorder")

        self.assertEqual(sorted_modules[0].pk, modules[4].pk)
        self.assertEqual(sorted_modules[1].pk, modules[3].pk)
        self.assertEqual(sorted_modules[2].pk, modules[2].pk)
        self.assertEqual(sorted_modules[3].pk, modules[1].pk)
        self.assertEqual(sorted_modules[4].pk, modules[0].pk)

    def test_sorting_validation_break_end_validation(self) -> None:
        # Break end cannot be before break start
        project: Project = ProjectFactory(owner=self.user)
        experiment: Experiment = ExperimentFactory(project=project)
        modules = FearConditioningModuleFactory.create_batch(5, experiment=experiment)

        break_mod = BreakStartModuleFactory(
            sortorder=0,
            experiment=experiment,
            end_module__sortorder=1,
        )

        # Fix sort order of test objects
        for index, mod in enumerate(modules):
            mod.sortorder = index + 2
            mod.save()

        # Put break end after break start
        json_data = {
            break_mod.end_module.pk: 0,
            break_mod.pk: 1,
            modules[0].pk: 2,
            modules[1].pk: 3,
            modules[2].pk: 4,
            modules[3].pk: 5,
            modules[4].pk: 6,
        }

        url = reverse(
            "experiments:module_sort",
            kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
        )

        resp = self.client.post(url, json_data, format="json")

        self.assertEqual(400, resp.status_code)

        self.assertEqual(
            resp.json()["message"],
            "Invalid configuration. Breaks must not end before they start.",
        )

    def test_sorting_validation_break_overlap_validation(self) -> None:
        # Breaks cannot overlap
        project: Project = ProjectFactory(owner=self.user)
        experiment: Experiment = ExperimentFactory(project=project)
        modules = FearConditioningModuleFactory.create_batch(5, experiment=experiment)

        break_mod_1 = BreakStartModuleFactory(
            sortorder=0,
            experiment=experiment,
            end_module__sortorder=1,
        )
        break_mod_2 = BreakStartModuleFactory(
            sortorder=2,
            experiment=experiment,
            end_module__sortorder=3,
        )
        break_mod_3 = BreakStartModuleFactory(
            sortorder=3,
            experiment=experiment,
            end_module__sortorder=3,
        )

        # Fix sort order of test objects
        for index, mod in enumerate(modules):
            mod.sortorder = index + 5
            mod.save()

        # Overlap the three breaks
        json_data = {
            break_mod_3.pk: 0,
            break_mod_1.pk: 1,
            break_mod_3.end_module.pk: 2,
            break_mod_1.end_module.pk: 3,
            break_mod_2.pk: 4,
            break_mod_2.end_module.pk: 5,
            modules[0].pk: 6,
            modules[1].pk: 7,
            modules[2].pk: 8,
            modules[3].pk: 9,
            modules[4].pk: 10,
        }

        url = reverse(
            "experiments:module_sort",
            kwargs={"project_pk": project.pk, "experiment_pk": experiment.pk},
        )

        resp = self.client.post(url, json_data, format="json")

        self.assertEqual(400, resp.status_code)

        self.assertEqual(
            resp.json()["message"],
            "Invalid configuration. Breaks must not overlap.",
        )


class ExportViewTest(TestCase):
    def setUp(self) -> None:
        self.user: User = UserFactory()
        self.user.grant_role("RESEARCHER")
        self.user.save()

        self.client.force_login(self.user)

        self.project = ProjectFactory(owner=self.user)
        self.experiment: Experiment = ExperimentFactory(
            project=self.project, code="DEMO1"
        )

    def test_get(self) -> None:
        url = reverse(
            "experiments:export",
            kwargs={"project_pk": self.project.pk, "experiment_pk": self.experiment.pk},
        )

        resp = self.client.get(url)

        self.assertEqual(200, resp.status_code)

    def test_download(self) -> None:
        url = reverse(
            "experiments:export_download",
            kwargs={"project_pk": self.project.pk, "experiment_pk": self.experiment.pk},
        )

        with freeze_time("20210101T1200"):
            resp = self.client.get(url)

        # Not actually checking the contents of the zip because it's hard to
        # test
        self.assertEqual(200, resp.status_code)
        self.assertEqual(
            resp.get("Content-Disposition"),
            "attachment; filename=DEMO1-20210101T120000Z.zip",
        )
