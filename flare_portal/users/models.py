from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models

from . import constants


class User(AbstractUser):
    roles = ArrayField(models.CharField(max_length=10, blank=False), default=list)

    @property
    def name(self) -> str:
        """
        Returns the most complete name of the user
        """
        parts = []

        if self.first_name:
            parts.append(self.first_name)

        if self.last_name:
            parts.append(self.last_name)

        name = " ".join(parts)

        if name:
            return name

        return ""

    @property
    def initials(self) -> str:
        """
        Returns the user's initials
        """
        letters = ""

        if self.first_name:
            letters += self.first_name[0]

        if self.last_name:
            letters += self.last_name[0]

        if letters:
            return letters.upper()

        return self.username[0].upper()

    def has_role(self, role_name: constants.Roles) -> bool:
        """
        Returns True if the user has the given role, False otherwise
        """
        return role_name in self.roles

    def grant_role(self, role_name: constants.Roles) -> None:
        """
        Grants the provided role to the user
        """
        roles = set(self.roles)
        roles.add(role_name)
        self.roles = list(roles)

    def revoke_role(self, role_name: constants.Roles) -> None:
        """
        Revokes the given role from the user
        """
        roles = set(self.roles)
        roles.discard(role_name)
        self.roles = list(roles)

    def get_roles_display(self) -> str:
        role_dict = dict(constants.ROLE_CHOICES)
        roles = [role_dict[role] for role in self.roles]
        return ", ".join(roles)

    def __str__(self) -> str:
        return self.name or self.username
