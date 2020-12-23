from typing import List, Union

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import URLPattern, URLResolver, include, path
from django.views.decorators.vary import vary_on_headers
from django.views.generic import TemplateView

from flare_portal.api import urls as api_urls
from flare_portal.experiments import urls as experiment_urls
from flare_portal.site_config import urls as site_config_urls
from flare_portal.users import urls as users_urls
from flare_portal.utils.cache import get_default_cache_control_decorator
from flare_portal.utils.urls import decorate_urlpatterns

# Private URLs are not meant to be cached.
private_urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("configuration/", include(site_config_urls)),
    path("", include(experiment_urls)),
    path("", include(users_urls)),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
]

private_urlpatterns = decorate_urlpatterns(private_urlpatterns, login_required)

urlpatterns: List[Union[URLPattern, URLResolver]] = [
    path("accounts/", include(users_urls.public_urlpatterns)),
    path("api/v1/", include(api_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()  # type: ignore
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )  # type:ignore

    urlpatterns += [
        # Add views for testing 404 and 500 templates
        path(
            "test404/",
            TemplateView.as_view(template_name="404.html"),
        ),
        path(
            "test500/",
            TemplateView.as_view(template_name="500.html"),
        ),
    ]

    # Try to install the django debug toolbar, if exists
    if apps.is_installed("debug_toolbar"):
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls))
        ] + urlpatterns  # type: ignore


# Set public URLs to use the "default" cache settings.
urlpatterns = decorate_urlpatterns(urlpatterns, get_default_cache_control_decorator())

# Set vary header to instruct cache to serve different version on different
# cookies, different request method (e.g. AJAX) and different protocol
# (http vs https).
urlpatterns = decorate_urlpatterns(
    urlpatterns,
    vary_on_headers(
        "Cookie", "X-Requested-With", "X-Forwarded-Proto", "Accept-Encoding"
    ),
)

# Join private and public URLs.
urlpatterns = private_urlpatterns + urlpatterns

# Error handlers
handler404 = "flare_portal.utils.views.page_not_found"
handler500 = "flare_portal.utils.views.server_error"
