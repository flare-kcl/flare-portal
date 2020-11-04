from django.test import TestCase

from ..factories import UserFactory
from ..models import User
from ..templatetags.user_tags import has_role


class HasRoleTagTest(TestCase):
    def test_role_required_tag(self) -> None:
        user: User = UserFactory()

        self.assertFalse(has_role(user, "ADMIN"))

        user.grant_role("ADMIN")

        self.assertTrue(has_role(user, "ADMIN"))
