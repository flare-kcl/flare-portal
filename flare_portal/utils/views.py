from django.views import defaults


def page_not_found(request, exception, template_name="404.html"):
    return defaults.page_not_found(request, exception, template_name)


def server_error(request, template_name="500.html"):
    return defaults.server_error(request, template_name)
