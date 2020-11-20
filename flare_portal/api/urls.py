from django.urls import path

from flare_portal.experiments.models import FearConditioningData

from . import views
from .registry import DataRegistry

registry = DataRegistry()

registry.register(FearConditioningData)

app_name = "api"
urlpatterns = [
    path("configuration/", views.configuration_api_view, name="configuration"),
] + registry.urls
