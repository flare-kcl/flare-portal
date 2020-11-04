from django import forms
from django.contrib import messages
from django.http import HttpResponse
from django.views.generic import ListView
from django.views.generic.edit import CreateView

from .models import Experiment, Project


class ProjectListView(ListView):
    context_object_name = "projects"
    model = Project


project_list_view = ProjectListView.as_view()


class ProjectCreateView(CreateView):
    model = Project
    fields = ["name", "description", "owner"]
    object = None

    def form_valid(self, form: forms.BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, f'Added new project "{self.object}"')
        return response


project_create_view = ProjectCreateView.as_view()


class ExperimentListView(ListView):
    context_object_name = "experiments"
    model = Experiment


experiment_list_view = ExperimentListView.as_view()
