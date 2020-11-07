from django.urls import path

from . import views

app_name = "api"
urlpatterns = [
    path("configuration/", views.configuration_api_view, name="configuration"),
]
