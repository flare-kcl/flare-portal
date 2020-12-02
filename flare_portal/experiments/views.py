from typing import Any

from django import forms
from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import pluralize
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView

from .forms import ExperimentForm, ParticipantBatchForm, ParticipantFormSet
from .models import Experiment, FearConditioningData, Project


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

    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        self.project = get_object_or_404(Project, pk=kwargs["project_pk"])
        return super().dispatch(*args, **kwargs)

    def get_queryset(self) -> QuerySet[Experiment]:
        return Experiment.objects.filter(project=self.project)

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["project"] = self.project
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
    fields = [
        "name",
        "description",
        "code",
        "owner",
        "trial_length",
        "rating_delay",
        "rating_scale_anchor_label_left",
        "rating_scale_anchor_label_center",
        "rating_scale_anchor_label_right",
    ]
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
    queryset = Experiment.objects.select_related("project").prefetch_related("modules")
    object: Experiment

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        # fmt: off
        context["modules"] = (
            self.object.modules  # type: ignore
            .select_subclasses()
            .select_related("experiment")
        )
        # fmt: on
        return context


experiment_detail_view = ExperimentDetailView.as_view()


class ParticipantCreateBatchView(FormView):
    form_class = ParticipantBatchForm
    template_name = "experiments/participant_create_batch_form.html"

    def get_success_url(self) -> str:
        return reverse(
            "experiments:participant_list",
            kwargs={
                "project_pk": self.kwargs["project_pk"],
                "experiment_pk": self.kwargs["experiment_pk"],
            },
        )

    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        self.experiment = get_object_or_404(Experiment, pk=kwargs["experiment_pk"])
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["experiment"] = self.experiment
        return context

    def form_valid(self, form: ParticipantBatchForm) -> HttpResponse:  # type: ignore
        form.save(experiment=self.experiment)
        return super().form_valid(form)


participant_create_batch_view = ParticipantCreateBatchView.as_view()


class ParticipantFormSetView(FormView):
    form_class = ParticipantFormSet  # type: ignore
    template_name = "experiments/participant_list.html"

    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        self.experiment = get_object_or_404(Experiment, pk=kwargs["experiment_pk"])
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self) -> dict:
        return {
            **super().get_form_kwargs(),
            "instance": self.experiment,
        }

    def get_success_url(self) -> str:
        return reverse(
            "experiments:participant_list",
            kwargs={
                "project_pk": self.kwargs["project_pk"],
                "experiment_pk": self.kwargs["experiment_pk"],
            },
        )

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["experiment"] = self.experiment
        context["participants"] = self.experiment.participants.all()
        return context

    def form_valid(self, formset: ParticipantFormSet) -> HttpResponse:  # type: ignore
        formset.save()  # type: ignore

        changes = []

        if new_count := len(formset.new_objects):  # type: ignore
            changes.append(f"Added {new_count} new participant{pluralize(new_count)}.")

        if changed_count := len(formset.changed_objects):  # type: ignore
            changes.append(
                f"Changed {changed_count} participant{pluralize(changed_count)}."
            )

        if deleted_count := len(formset.deleted_objects):  # type: ignore
            changes.append(
                f"Deleted {deleted_count} participant{pluralize(deleted_count)}."
            )

        messages.success(self.request, " ".join(changes))
        return super().form_valid(formset)


participant_formset_view = ParticipantFormSetView.as_view()


class FearConditioningDataListView(ListView):
    context_object_name = "data"
    data_type = FearConditioningData
    template_name = "experiments/data_list.html"

    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        self.experiment = get_object_or_404(Experiment, pk=kwargs["experiment_pk"])
        return super().dispatch(*args, **kwargs)

    def get_queryset(self) -> QuerySet[FearConditioningData]:
        return FearConditioningData.objects.filter(
            module__experiment=self.experiment
        ).select_related("participant", "module")

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["experiment"] = self.experiment
        context["data_type"] = self.data_type
        return context


fear_conditioning_data_list_view = FearConditioningDataListView.as_view()


class FearConditioningDataDetailView(DetailView):
    context_object_name = "data"
    data_type = FearConditioningData
    pk_url_kwarg = "data_pk"
    queryset = FearConditioningData.objects.select_related("participant")
    template_name = "experiments/data_detail.html"

    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        self.experiment = get_object_or_404(Experiment, pk=kwargs["experiment_pk"])
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["experiment"] = self.experiment
        context["data_type"] = self.data_type
        return context


fear_conditioning_data_detail_view = FearConditioningDataDetailView.as_view()
