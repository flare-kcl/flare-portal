from django.urls import include, path

from flare_portal.users.decorators import (
    has_researcher_access,
    role_required,
)
from flare_portal.utils.urls import decorate_urlpatterns

from . import views
from .registry import data_viewset_registry, module_registry

app_name = "experiments"


urlpatterns = [
    path("projects/", views.project_list_view, name="project_list"),
    path("projects/add/", views.project_create_view, name="project_create"),
]

project_urlpatterns = [
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
        "projects/<int:project_pk>/experiments/<int:experiment_pk>/export/",
        views.export_view,
        name="export",
    ),
    path(
        "projects/<int:project_pk>/experiments/<int:experiment_pk>/export/download/",
        views.export_download_view,
        name="export_download",
    ),
    path(
        "projects/<int:project_pk>/experiments/<int:experiment_pk>/sort-modules/",
        views.module_sort_view,
        name="module_sort",
    ),
    path(
        "projects/<int:project_pk>/experiments/<int:experiment_pk>/participants/",
        views.participant_formset_view,
        name="participant_list",
    ),
    path(
        "projects/<int:project_pk>/experiments/<int:experiment_pk>/"
        "participants/add-batch/",
        views.participant_create_batch_view,
        name="participant_create_batch",
    ),
    path(
        "projects/<int:project_pk>/experiments/<int:experiment_pk>/"
        "participants/upload/",
        views.participant_upload_view,
        name="participant_upload",
    ),
    path(
        "projects/<int:project_pk>/experiments/<int:experiment_pk>/"
        "participants/<int:participant_pk>/delete/",
        views.participant_delete_view,
        name="participant_delete",
    ),
    path(
        "projects/<int:project_pk>/experiments/<int:experiment_pk>/"
        "participants/<str:participant_pks>/delete-bulk/",
        views.participant_bulk_delete_view,
        name="participant_delete_batch",
    ),
    path(
        "projects/<int:project_pk>/experiments/<int:experiment_pk>/"
        "participants/<int:participant_pk>/detail/",
        views.participant_detail_view,
        name="participant_detail",
    ),
    path(
        "projects/<int:project_pk>/leave/",
        views.researcher_leave_view,
        name="researcher_leave",
    ),
    path("", include((module_registry.urls, "modules"))),
    path("", include((data_viewset_registry.urls, "data"))),
]

project_owner_urlpatterns = [
    path(
        "projects/<int:project_pk>/researchers/",
        views.researcher_add_view,
        name="researcher_list",
    ),
    path(
        "projects/<int:project_pk>/researchers/<int:researcher_pk>/delete/",
        views.researcher_delete_view,
        name="researcher_delete",
    ),
]

project_urlpatterns = decorate_urlpatterns(project_urlpatterns, has_researcher_access)
project_owner_urlpatterns = decorate_urlpatterns(
    project_owner_urlpatterns, has_researcher_access, True
)

urlpatterns = decorate_urlpatterns(
    urlpatterns + project_urlpatterns + project_owner_urlpatterns,
    role_required,
    "RESEARCHER",
)
