from django.urls import path

from . import views
from .registry import module_data_registry

app_name = "api"
urlpatterns = [
    path("configuration/", views.configuration_api_view, name="configuration"),
] + module_data_registry.urls
