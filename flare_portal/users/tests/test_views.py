from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..factories import UserFactory

User = get_user_model()


class UserIndexViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_login(self.user)

    def test_get(self) -> None:
        resp = self.client.get(reverse("users:user_list"))
        self.assertEqual(200, resp.status_code)


class UserCreateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_login(self.user)

    def test_create_user(self) -> None:
        form_data = {
            "username": "john.smith",
            "first_name": "John",
            "last_name": "Smith",
            "email": "john@smith.com",
            "password": "hunter2",
            "password2": "hunter2",
            "roles": ["RESEARCHER"],
        }

        resp = self.client.post(reverse("users:user_create"), form_data)

        self.assertRedirects(resp, reverse("users:user_list"))

        user = User.objects.get(email="john@smith.com")

        self.assertEqual(user.first_name, form_data["first_name"])
        self.assertEqual(user.last_name, form_data["last_name"])
        self.assertTrue(user.has_role("RESEARCHER"))
