from django.test import TestCase
from django.urls import reverse

from ..factories import UserFactory
from ..models import User


class UserAuthorizationTest(TestCase):
    def setUp(self) -> None:
        self.user: User = UserFactory()
        self.client.force_login(self.user)

    def test_only_admins_can_access_user_management(self) -> None:
        resp = self.client.get(reverse("users:user_list"))
        self.assertEqual(302, resp.status_code)

        resp = self.client.get(reverse("users:user_create"))
        self.assertEqual(302, resp.status_code)

        resp = self.client.get(
            reverse("users:user_update", kwargs={"pk": self.user.pk})
        )
        self.assertEqual(302, resp.status_code)

        self.user.grant_role("ADMIN")
        self.user.save()

        resp = self.client.get(reverse("users:user_list"))
        self.assertEqual(200, resp.status_code)

        resp = self.client.get(reverse("users:user_create"))
        self.assertEqual(200, resp.status_code)

        resp = self.client.get(
            reverse("users:user_update", kwargs={"pk": self.user.pk})
        )
        self.assertEqual(200, resp.status_code)

    def test_superadmins_can_access_everything(self) -> None:
        self.user.is_superuser = True
        self.user.save()

        resp = self.client.get(reverse("users:user_list"))
        self.assertEqual(200, resp.status_code)

        resp = self.client.get(reverse("users:user_create"))
        self.assertEqual(200, resp.status_code)


class UserListViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("ADMIN")
        self.user.save()
        self.client.force_login(self.user)

    def test_get(self) -> None:
        resp = self.client.get(reverse("users:user_list"))
        self.assertEqual(200, resp.status_code)


class UserCreateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("ADMIN")
        self.user.save()
        self.client.force_login(self.user)

    def test_create_user(self) -> None:
        form_data = {
            "username": "john.smith",
            "first_name": "John",
            "last_name": "Smith",
            "email": "john@smith.com",
            "job_title": "Research assistant",
            "affiliation": "Torchbox",
            "password1": "hunter2",
            "password2": "hunter2",
            "roles": ["RESEARCHER"],
        }

        resp = self.client.post(reverse("users:user_create"), form_data, follow=True)

        self.assertRedirects(resp, reverse("users:user_list"))

        user = User.objects.get(email="john@smith.com")

        self.assertEqual(user.first_name, form_data["first_name"])
        self.assertEqual(user.last_name, form_data["last_name"])
        self.assertEqual(user.job_title, form_data["job_title"])
        self.assertEqual(user.affiliation, form_data["affiliation"])
        self.assertTrue(user.has_role("RESEARCHER"))

        self.assertEqual(
            str(list(resp.context["messages"])[0]), f'Added new user "{user}"'
        )


class UserUpdateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("ADMIN")
        self.user.save()
        self.client.force_login(self.user)

    def test_update_user(self) -> None:
        user: User = UserFactory()
        user.set_password("dontchangeme")
        user.grant_role("ADMIN")
        user.save()

        form_data = {
            "username": "john.smith",
            "first_name": "John",
            "last_name": "Smith",
            "email": "john@smith.com",
            "job_title": "Research assistant",
            "affiliation": "Torchbox",
            "is_active": False,
            "password1": "",
            "password2": "",
            "roles": ["RESEARCHER"],
        }

        resp = self.client.post(
            reverse("users:user_update", kwargs={"pk": user.pk}), form_data, follow=True
        )

        self.assertRedirects(resp, reverse("users:user_list"))

        user = User.objects.get(email="john@smith.com")

        # Other bits should change
        self.assertEqual(user.username, form_data["username"])
        self.assertEqual(user.first_name, form_data["first_name"])
        self.assertEqual(user.last_name, form_data["last_name"])
        self.assertEqual(user.job_title, form_data["job_title"])
        self.assertEqual(user.affiliation, form_data["affiliation"])
        self.assertTrue(user.has_role("RESEARCHER"))
        self.assertEqual(1, len(user.roles))
        self.assertFalse(user.is_active)

        # Password shouldn't change because the password fields are empty
        self.assertTrue(user.check_password("dontchangeme"))

        self.assertEqual(
            str(list(resp.context["messages"])[0]), f'Updated user "{user}"'
        )


class UserDeleteViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("ADMIN")
        self.user.save()
        self.client.force_login(self.user)

    def test_delete_user(self) -> None:
        user: User = UserFactory()
        resp = self.client.get(reverse("users:user_delete", kwargs={"pk": user.pk}))

        self.assertEqual(200, resp.status_code)

        resp = self.client.post(
            reverse("users:user_delete", kwargs={"pk": user.pk}), follow=True
        )

        self.assertRedirects(resp, reverse("users:user_list"))

        self.assertEqual(0, User.objects.filter(pk=user.pk).count())

        self.assertEqual(
            str(list(resp.context["messages"])[0]), f'Deleted user "{user}"'
        )
