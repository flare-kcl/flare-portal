import sys
from functools import wraps
from typing import Any, Callable

from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from flare_portal.site_config.models import SiteConfiguration
from flare_portal.users.models import User

from . import constants


def role_required(
    function: Callable,
    role_name: constants.Roles,
    login_url: str = "",
    redirect_field_name: str = REDIRECT_FIELD_NAME,
) -> Callable:
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def _wrapped_view(
            request: HttpRequest, *args: Any, **kwargs: Any
        ) -> HttpResponse:
            if (
                request.user.is_authenticated
                and isinstance(request.user, User)
                and (request.user.has_role(role_name) or request.user.is_superuser)
            ):
                return view_func(request, *args, **kwargs)

            messages.warning(request, "You don't have permission to access that page.")
            return redirect("home")

        return _wrapped_view

    return decorator(function)


def can_user_view_project(
    project_pk: int, user: User, owner_only: bool = False
) -> bool:
    return user.get_projects(owner_only=owner_only).filter(pk=project_pk).exists()


def has_researcher_access(function: Callable, owner_only: bool = False) -> Callable:
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def _wrapped_view(
            request: HttpRequest, *args: Any, **kwargs: Any
        ) -> HttpResponse:
            if request.user.is_authenticated and isinstance(request.user, User):
                if project_pk := kwargs.get("project_pk"):
                    if request.user.is_admin or can_user_view_project(
                        project_pk, request.user, owner_only
                    ):
                        return view_func(request, *args, **kwargs)

            messages.warning(
                request, "You don't have permission to access that project."
            )

            return redirect("experiments:project_list")

        return _wrapped_view

    return decorator(function)


IGNORE_RESEARCHER_TERMS = "test" in sys.argv


def must_accept_terms(function: Callable) -> Callable:
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def _wrapped_view(
            request: HttpRequest, *args: Any, **kwargs: Any
        ) -> HttpResponse:
            if request.user.is_authenticated and isinstance(request.user, User):
                config = SiteConfiguration.get_solo()
                if (
                    # Check if the user has agreed to the current terms of
                    # service
                    (
                        request.user.agreed_terms_at is not None
                        and config.researcher_terms_updated_at is not None
                        and (
                            request.user.agreed_terms_at
                            > config.researcher_terms_updated_at
                        )
                    )
                    # Or bypass if terms of service is not set
                    or (config.researcher_terms_updated_at is None)
                    # Or bypass explicitly
                    or IGNORE_RESEARCHER_TERMS
                ):
                    return view_func(request, *args, **kwargs)

            return redirect("researcher_terms_form")

        return _wrapped_view

    return decorator(function)
