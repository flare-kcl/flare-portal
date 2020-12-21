from django.urls import path

from . import views

app_name = "site_config"

urlpatterns = [
    path("update/", views.site_configuration_update_view, name="update"),
]
