from django import template

from .. import constants
from ..models import User

register = template.Library()


@register.filter
def has_role(user: User, role_name: constants.Roles) -> bool:
    return user.has_role(role_name)
