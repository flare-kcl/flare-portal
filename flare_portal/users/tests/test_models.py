from django.test import TestCase

from ..factories import UserFactory
from ..models import User


class UserTest(TestCase):
    def test_roles(self) -> None:
        user: User = UserFactory()

        user.grant_role("ADMIN")
        user.save()

        self.assertTrue(user.has_role("ADMIN"))
        self.assertFalse(user.has_role("RESEARCHER"))

        user.revoke_role("ADMIN")
        self.assertFalse(user.has_role("ADMIN"))

    def test_role_uniqueness(self) -> None:
        """
        Adding multiple of the same role is mitigated
        """

        user: User = UserFactory()
        user.grant_role("RESEARCHER")
        user.grant_role("RESEARCHER")
        user.grant_role("ADMIN")
        user.grant_role("ADMIN")
        user.save()

        self.assertEqual(2, len(user.roles))
        self.assertIn("RESEARCHER", user.roles)
        self.assertIn("ADMIN", user.roles)
