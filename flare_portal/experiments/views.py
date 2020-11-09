from typing import Any

from django import forms
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import ExperimentForm
from .models import Experiment, Project


class ProjectListView(ListView):
    context_object_name = "projects"
    model = Project


project_list_view = ProjectListView.as_view()


class ProjectCreateView(CreateView):
    model = Project
    fields = ["name", "description", "owner"]
    object: Project

    def get_initial(self) -> dict:
        return {"owner": self.request.user.pk}

    def form_valid(self, form: forms.BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, f'Added new project "{self.object}"')
        return response


project_create_view = ProjectCreateView.as_view()


class ProjectUpdateView(UpdateView):
    context_object_name = "project"
    fields = ["name", "description", "owner"]
    model = Project
    object: Project
    pk_url_kwarg = "project_pk"
    template_name = "experiments/project_update_form.html"

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

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        return context


experiment_list_view = ExperimentListView.as_view()


class ExperimentCreateView(CreateView):
    model = Experiment
    form_class = ExperimentForm
    object: Experiment

    def get_initial(self) -> dict:
        return {"project": self.kwargs["project_pk"], "owner": self.request.user.pk}

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        return context

    def form_valid(self, form: forms.BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, f'Added new experiment "{self.object}"')
        return response


experiment_create_view = ExperimentCreateView.as_view()


class ExperimentUpdateView(UpdateView):
    fields = ["name", "description", "code", "owner"]
    object: Experiment
    pk_url_kwarg = "experiment_pk"
    queryset = Experiment.objects.select_related("project")
    template_name = "experiments/experiment_update_form.html"

    def form_valid(self, form: forms.BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, f'Updated experiment "{self.object}"')
        return response


experiment_update_view = ExperimentUpdateView.as_view()


class ExperimentDeleteView(DeleteView):
    context_object_name = "experiment"
    model = Experiment
    pk_url_kwarg = "experiment_pk"

    def get_success_url(self) -> str:
        return reverse(
            "experiments:experiment_list",
            kwargs={"project_pk": self.kwargs["project_pk"]},
        )

    def delete(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        experiment = self.get_object()
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, f'Deleted experiment "{experiment}"')
        return response


experiment_delete_view = ExperimentDeleteView.as_view()


class ExperimentDetailView(DetailView):
    context_object_name = "experiment"
    pk_url_kwarg = "experiment_pk"
    queryset = Experiment.objects.select_related("project")


experiment_detail_view = ExperimentDetailView.as_view()
