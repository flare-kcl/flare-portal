from django.urls import path

from . import views

app_name = "experiments"

urlpatterns = [path("projects/", views.project_list_view, name="project_list")]
