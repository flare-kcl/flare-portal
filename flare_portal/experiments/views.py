from itertools import combinations
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

from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import (
    ExperimentCreateForm,
    ExperimentForm,
    ParticipantBatchForm,
    ParticipantDeleteForm,
    ParticipantFormSet,
    ParticipantUploadForm,
)
from .models import BreakEndModule, Experiment, Project, Participant


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
    form_class = ExperimentCreateForm
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
    form_class = ExperimentForm
    object: Experiment
    pk_url_kwarg = "experiment_pk"
    queryset = Experiment.objects.select_related("project")
    template_name = "experiments/experiment_form.html"

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


class ParticipantDeleteView(FormView):
    form_class = ParticipantDeleteForm
    template_name = "experiments/participant_delete_form.html"

    def get_success_url(self) -> str:
        return reverse(
            "experiments:participant_list",
            kwargs={
                "project_pk": self.kwargs["project_pk"],
                "experiment_pk": self.kwargs["experiment_pk"],
            },
        )

    def get_form_kwargs(self):
        kwargs = super(ParticipantDeleteView, self).get_form_kwargs()
        kwargs["participant"] = self.participant
        return kwargs

    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        self.experiment = get_object_or_404(Experiment, pk=kwargs["experiment_pk"])
        self.participant = get_object_or_404(Participant, pk=kwargs["participant_pk"])
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["experiment"] = self.experiment
        context["participant"] = self.participant
        return context

    def form_valid(self, form: ParticipantDeleteForm) -> HttpResponse:  # type: ignore
        # Attempt Delete
        form.save()

        # Add message
        messages.success(
            self.request,
            f"Particpant {self.participant.participant_id} deleted!",
        )

        # Return redirect
        return super().form_valid(form)


participant_delete_view = ParticipantDeleteView.as_view()


class ParticipantUploadView(FormView):
    form_class = ParticipantUploadForm
    template_name = "experiments/participant_upload_form.html"

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

    def form_valid(self, form: ParticipantUploadForm) -> HttpResponse:  # type: ignore
        # Parse Uploaded file
        participants, row_count = form.save(experiment=self.experiment)

        # If successful then add a message
        messages.success(
            self.request, f"{len(participants)}/{row_count} Participants Uploaded"
        )

        return super().form_valid(form)


participant_upload_view = ParticipantUploadView.as_view()


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


class ModuleSortView(APIView):
    """
    API Endpoint to handle module sorting
    """

    def post(
        self, request: Request, project_pk: int, experiment_pk: int, format: str = None
    ) -> Response:
        experiment = get_object_or_404(
            Experiment.objects.prefetch_related("modules"), pk=experiment_pk
        )
        all_modules = {
            mod.pk: mod
            for mod in experiment.modules.select_subclasses()  # type: ignore
        }

        # Dict[module_pk, sortorder]
        module_mapping = request.data

        # Parse and build the list of sorted modules based on the request
        sorted_modules = []

        try:
            for module_pk, _ in sorted(
                module_mapping.items(), key=lambda item: item[1]
            ):
                sorted_modules.append(all_modules[int(module_pk)])
        except ValueError:
            raise ParseError()
        except KeyError:
            raise ValidationError(
                f"Module with id {module_pk} not found in experiment with "
                f"id {experiment_pk}."
            )

        # Set ordering
        for index, module in enumerate(sorted_modules):
            module.sortorder = index

        # Validate ordering

        # Check break end modules dont come before their corresponding break
        # start modules
        for end_module in filter(
            lambda m: isinstance(m, BreakEndModule), sorted_modules
        ):
            start_module = all_modules[end_module.start_module_id]
            if end_module.sortorder <= start_module.sortorder:
                return Response(
                    {
                        "message": "Invalid configuration. Breaks must not end "
                        "before they start."
                    },
                    status=400,
                )

        # Check breaks dont overlap
        break_ranges = []
        for end_module in filter(
            lambda m: isinstance(m, BreakEndModule), sorted_modules
        ):
            start_module = all_modules[end_module.start_module_id]
            break_ranges.append(
                set(range(start_module.sortorder, end_module.sortorder))
            )

        if len(break_ranges) > 1:
            # Need more than one break for this to ever be true
            for set_a, set_b in combinations(break_ranges, 2):
                # Check if any two breaks overlap
                # This is checking if any two breaks intersect
                # A: {1, 2, 3}
                # B: {2, 3, 4}
                # C: {5}
                # This code will check A&B, A&C, then B&C
                # NB. This is NOT the same as checking for the intersection of
                # all breaks combined. e.g. `set.intersection(*break_ranges)`
                if set_a.intersection(set_b):
                    return Response(
                        {"message": "Invalid configuration. Breaks must not overlap."},
                        status=400,
                    )

        # Save ordering
        for module in sorted_modules:
            module.save()

        return Response({"message": "Saved ordering."})


module_sort_view = ModuleSortView.as_view()
