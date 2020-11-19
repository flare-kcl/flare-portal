from django.urls import include, path

from flare_portal.users.decorators import role_required
from flare_portal.utils.urls import decorate_urlpatterns

from . import models, views
from .registry import ModuleRegistry

app_name = "experiments"

registry = ModuleRegistry()

registry.register(models.FearConditioningModule)

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
        "projects/<int:project_pk>/experiments/add/",
        views.experiment_create_view,
        name="experiment_create",
    ),
    path(
        "projects/<int:project_pk>/experiments/<int:experiment_pk>/",
        views.experiment_detail_view,
        name="experiment_detail",
    ),
    path(
        "projects/<int:project_pk>/experiments/<int:experiment_pk>/edit/",
        views.experiment_update_view,
        name="experiment_update",
    ),
    path(
        "projects/<int:project_pk>/experiments/<int:experiment_pk>/delete/",
        views.experiment_delete_view,
        name="experiment_delete",
    ),
    path(
        "projects/<int:project_pk>/experiments/<int:experiment_pk>/participants/",
        views.participant_list_view,
        name="participant_list",
    ),
    path(
        "projects/<int:project_pk>/experiments/<int:experiment_pk>/"
        "participants/add-batch/",
        views.participant_create_batch_view,
        name="participant_create_batch",
    ),
    path("", include((registry.urls, "modules"))),
]

urlpatterns = decorate_urlpatterns(urlpatterns, role_required, "RESEARCHER")
