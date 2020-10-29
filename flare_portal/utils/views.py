from django.http import HttpRequest, HttpResponse
from django.views import defaults


def page_not_found(
    request: HttpRequest, exception: Exception, template_name: str = "404.html"
) -> HttpResponse:
    return defaults.page_not_found(request, exception, template_name)


def server_error(request: HttpRequest, template_name: str = "500.html") -> HttpResponse:
    return defaults.server_error(request, template_name)
