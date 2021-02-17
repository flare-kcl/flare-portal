from functools import wraps
from typing import Any, Callable

from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from . import constants
from flare_portal.users.models import User


def role_required(
    function: Callable,
    role_name: constants.Roles,
    login_url: str = None,
    redirect_field_name: str = REDIRECT_FIELD_NAME,
) -> Callable:
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def _wrapped_view(
            request: HttpRequest, *args: Any, **kwargs: Any
        ) -> HttpResponse:
            if request.user.is_authenticated and (
                request.user.has_role(role_name) or request.user.is_superuser
            ):
                return view_func(request, *args, **kwargs)

            messages.warning(request, "You don't have permission to access that page.")
            return redirect("home")

        return _wrapped_view

    return decorator(function)


def has_researcher_access(
    function: Callable,
    owner_only: bool = False,
    login_url: str = None,
    redirect_field_name: str = REDIRECT_FIELD_NAME,
) -> Callable:
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def _wrapped_view(
            request: HttpRequest, *args: Any, **kwargs: Any
        ) -> HttpResponse:
            if isinstance(request.user, User):
                if project_pk := kwargs.get("project_pk"):
                    # Get all the projects that the user can access.
                    user_projects = request.user.get_projects(
                        owner_only=owner_only
                    ).values_list("id", flat=True)

                    if project_pk in user_projects or request.user.is_admin:
                        return view_func(request, *args, **kwargs)

            messages.warning(
                request, "You don't have permission to access that project."
            )
            return redirect("experiments:project_list")

        return _wrapped_view

    return decorator(function)
