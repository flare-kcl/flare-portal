from django.urls import path

from . import views
from .registry import data_api_registry

app_name = "api"
urlpatterns = [
    path("configuration/", views.configuration_api_view, name="configuration"),
    path("submission/", views.submission_api_view, name="submission"),
] + data_api_registry.urls
