from django.shortcuts import reverse
from django.test import TestCase

from ..factories import UserFactory


class UserIndexViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)

    def test_get(self):
        resp = self.client.get(reverse("users:user_list"))
        self.assertEqual(200, resp.status_code)
