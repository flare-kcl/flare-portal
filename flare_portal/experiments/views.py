from django.views.generic import ListView

from .models import Project


class ProjectListView(ListView):
    context_object_name = "projects"
    model = Project


project_list_view = ProjectListView.as_view()
