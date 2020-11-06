from django.urls import path

from . import views

app_name = "experiments"

urlpatterns = [
    path("projects/", views.project_list_view, name="project_list"),
    path("projects/add/", views.project_create_view, name="project_create"),
    path(
        "projects/<int:project_pk>/edit/",
        views.project_update_view,
        name="project_update",
    ),
    path(
        "projects/<int:project_pk>/delete/",
        views.project_delete_view,
        name="project_delete",
    ),
    path(
        "projects/<int:project_pk>/", views.experiment_list_view, name="experiment_list"
    ),
    path(
        "projects/<int:project_pk>/experiment/add/",
        views.experiment_create_view,
        name="experiment_create",
    ),
    path(
        "projects/<int:project_pk>/experiment/<int:experiment_pk>/",
        views.experiment_detail_view,
        name="experiment_detail",
    ),
    path(
        "projects/<int:project_pk>/experiment/<int:experiment_pk>/edit/",
        views.experiment_update_view,
        name="experiment_update",
    ),
    path(
        "projects/<int:project_pk>/experiment/<int:experiment_pk>/delete/",
        views.experiment_delete_view,
        name="experiment_delete",
    ),
]
