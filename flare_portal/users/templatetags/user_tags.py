from django import template

from .. import constants
from ..models import User

register = template.Library()


@register.filter
def has_role(user: User, role_name: constants.Roles) -> bool:
    """Returns true if the user has the given role, or if they're a superuser"""
    return user.has_role(role_name) or user.is_superuser
