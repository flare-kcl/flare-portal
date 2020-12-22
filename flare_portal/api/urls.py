from django.urls import path

from . import views
from .registry import data_api_registry

app_name = "api"
urlpatterns = [
    path("configuration/", views.configuration_api_view, name="configuration"),
    path(
        "terms-and-conditions/",
        views.terms_and_conditions_api_view,
        name="terms_and_conditions",
    ),
] + data_api_registry.urls
