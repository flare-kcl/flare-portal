from typing import Any

from django import forms
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

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


class ProjectUpdateView(UpdateView):
    context_object_name = "project"
    fields = ["name", "description", "owner"]
    model = Project
    object = None
    pk_url_kwarg = "project_pk"

    def form_valid(self, form: forms.BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, f'Updated project "{self.object}"')
        return response


project_update_view = ProjectUpdateView.as_view()


class ProjectDeleteView(DeleteView):
    context_object_name = "project"
    model = Project
    pk_url_kwarg = "project_pk"
    success_url = reverse_lazy("experiments:project_list")

    def delete(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        project = self.get_object()
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, f'Deleted project "{project}"')
        return response


project_delete_view = ProjectDeleteView.as_view()


class ExperimentListView(ListView):
    context_object_name = "experiments"
    model = Experiment


experiment_list_view = ExperimentListView.as_view()