from functools import wraps
from typing import Any, Callable

from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from . import constants


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
