from django.test import TestCase
from django.urls import reverse

from ..factories import UserFactory


class UserIndexViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_login(self.user)

    def test_get(self) -> None:
        resp = self.client.get(reverse("users:user_list"))
        self.assertEqual(200, resp.status_code)
