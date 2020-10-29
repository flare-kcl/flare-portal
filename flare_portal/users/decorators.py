from functools import wraps
from typing import Any, Callable
from urllib.parse import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpRequest, HttpResponse
from django.shortcuts import resolve_url

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
            if request.user.is_authenticated and request.user.has_role(role_name):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if (not login_scheme or login_scheme == current_scheme) and (
                not login_netloc or login_netloc == current_netloc
            ):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login

            messages.warning(request, "You don't have permission to access that page.")
            return redirect_to_login(path, resolved_login_url, redirect_field_name)

        return _wrapped_view

    return decorator(function)
