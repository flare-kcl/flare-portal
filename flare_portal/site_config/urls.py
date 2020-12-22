from django.urls import path

from flare_portal.users.decorators import role_required
from flare_portal.utils.urls import decorate_urlpatterns

from . import views

app_name = "site_config"

urlpatterns = [
    path("update/", views.site_configuration_update_view, name="update"),
]

urlpatterns = decorate_urlpatterns(urlpatterns, role_required, "ADMIN")
