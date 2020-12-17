from typing import Any, Callable, Dict, List, Optional, Type

from django import forms
from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import URLPattern, path, reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .models import (
    BaseData,
    BaseModule,
    BasicInfoData,
    BasicInfoModule,
    Experiment,
    FearConditioningData,
    FearConditioningModule,
    Participant,
)


class ModuleViewMixin:
    context_object_name = "module"

    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        self.experiment = get_object_or_404(Experiment, pk=kwargs["experiment_pk"])
        return super().dispatch(*args, **kwargs)  # type: ignore

    def get_success_url(self) -> str:
        return reverse(
            "experiments:experiment_detail",
            kwargs={
                "project_pk": self.experiment.project_id,
                "experiment_pk": self.experiment.pk,
            },
        )

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)  # type: ignore
        context["experiment"] = self.experiment

        if module_type := getattr(self, "model", None):
            context["module_type"] = module_type
        elif form_class := getattr(self, "form_class", None):
            context["module_type"] = form_class.Meta.model
        return context


class ModuleCreateViewMixin(ModuleViewMixin):
    template_name = "experiments/module_form.html"

    def get_initial(self) -> dict:
        return {"experiment": self.experiment.pk}

    def form_valid(self, form: forms.BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)  # type:ignore
        messages.success(
            self.request,  # type:ignore
            f"Added {self.object.get_module_name()} module",  # type:ignore
        )
        return response


class ModuleUpdateViewMixin(ModuleViewMixin):
    template_name = "experiments/module_form.html"

    def form_valid(self, form: forms.BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)  # type:ignore
        messages.success(
            self.request,  # type:ignore
            f"Updated {self.object.get_module_name()} module",  # type:ignore
        )
        return response


class ModuleDeleteViewMixin(ModuleViewMixin):
    pk_url_kwarg = "module_pk"
    template_name = "experiments/module_confirm_delete.html"

    def delete(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:  # type: ignore
        module = self.get_object()  # type:ignore
        response = super().delete(request, *args, **kwargs)  # type:ignore
        module_name = module.get_module_name()
        messages.success(self.request, f"Deleted {module_name} module")  # type:ignore
        return response


class ModuleRegistry:
    """
    Registry for module types

    Registering a module type to this registry will add it to the list of
    module types that can be added to an experiment.
    """

    def __init__(self) -> None:
        self.modules: List[Type[BaseModule]] = []
        self.urls: List[URLPattern] = []
        self.views: Dict[str, Callable] = {}

    def register(self, module_class: Type[BaseModule]) -> None:
        """
        Dynamically creates views for a module

        This will create a CreateView, UpdateView, and DeleteView for the
        registered module type
        """
        module_camel_case = module_class.get_module_camel_case()

        self.modules.append(module_class)

        # CreateView
        class CreateMeta:
            model = module_class
            fields = [
                f.name for f in module_class._meta.fields if f.name != "sortorder"
            ]
            widgets = {
                "experiment": forms.HiddenInput(),
            }

        form_class = type(
            f"{module_camel_case}Form", (forms.ModelForm,), {"Meta": CreateMeta}
        )

        create_view_class: CreateView = type(  # type: ignore
            f"{module_camel_case}CreateView",
            (
                ModuleCreateViewMixin,
                CreateView,
            ),
            {"form_class": form_class},
        )
        create_view_name = module_class.get_create_path_name()

        self.views[create_view_name] = create_view_class.as_view()
        self.urls.append(
            path(
                module_class.get_create_path(),
                self.views[create_view_name],
                name=create_view_name,
            )
        )

        # Update view
        update_view_class: UpdateView = type(  # type: ignore
            f"{module_camel_case}UpdateView",
            (
                ModuleUpdateViewMixin,
                UpdateView,
            ),
            {
                "model": module_class,
                "fields": [
                    f.name
                    for f in module_class._meta.fields
                    if f.name not in ["sortorder", "experiment"]
                ],
                "pk_url_kwarg": "module_pk",
            },
        )
        update_view_name = module_class.get_update_path_name()

        self.views[update_view_name] = update_view_class.as_view()
        self.urls.append(
            path(
                module_class.get_update_path(),
                self.views[update_view_name],
                name=update_view_name,
            )
        )

        # Delete view
        delete_view_class: DeleteView = type(  # type: ignore
            f"{module_camel_case}DeleteView",
            (ModuleDeleteViewMixin, DeleteView),
            {"model": module_class},
        )
        delete_view_name = module_class.get_delete_path_name()

        self.views[delete_view_name] = delete_view_class.as_view()
        self.urls.append(
            path(
                module_class.get_delete_path(),
                self.views[delete_view_name],
                name=delete_view_name,
            )
        )


module_registry = ModuleRegistry()

module_registry.register(BasicInfoModule)
module_registry.register(FearConditioningModule)


class DataViewMixin:
    data_type: Type[BaseData]

    def get_data_type(self) -> Type[BaseData]:
        return self.data_type

    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        self.experiment = get_object_or_404(Experiment, pk=kwargs["experiment_pk"])
        return super().dispatch(*args, **kwargs)  # type: ignore

    def get_queryset(self) -> QuerySet[BaseData]:
        data_type = self.get_data_type()
        return (
            data_type.objects.filter(module__experiment=self.experiment)
            .order_by("pk")
            .select_related("participant", "module")
        )

    def get_context_data(self, **kwargs: Any) -> dict:
        data_type = self.get_data_type()
        context = super().get_context_data(**kwargs)  # type: ignore
        context["experiment"] = self.experiment
        context["data_type"] = data_type
        return context


class DataListView(DataViewMixin, ListView):
    context_object_name = "data"
    template_name = "experiments/data_list.html"
    participant: Optional[Participant] = None

    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        if participant_id := self.request.GET.get("participant"):
            try:
                self.participant = Participant.objects.get(
                    participant_id=participant_id
                )
            except Participant.DoesNotExist:
                pass

        return super().dispatch(*args, **kwargs)

    def get_queryset(self) -> QuerySet[BaseData]:
        qs = super().get_queryset()

        if self.participant:
            return qs.filter(participant=self.participant)

        return qs

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)

        if self.participant:
            context["participant"] = self.participant

        return context


class DataDetailView(DataViewMixin, DetailView):
    context_object_name = "data"
    pk_url_kwarg = "data_pk"
    template_name = "experiments/data_detail.html"


class DataViewsetRegistry:
    """
    Registry for module data types

    Registering a module data type to this registry will make its data viewable
    on the portal.
    """

    def __init__(self) -> None:
        self.data_models: List[Type[BaseData]] = []
        self.urls: List[URLPattern] = []
        self.views: Dict[str, Callable] = {}

    def register(
        self, data_model: Type[BaseData], list_view_class: Type[DataListView] = None
    ) -> None:
        module_camel_case = data_model.get_module_camel_case()

        self.data_models.append(data_model)

        # ListView
        list_view_name = data_model.get_list_path_name()
        if list_view_class is not None:
            self.views[list_view_name] = list_view_class.as_view()
        else:
            self.views[list_view_name]: DataListView = type(  # type: ignore
                f"{module_camel_case}ListView",
                (DataListView,),
                {"data_type": data_model},
            ).as_view()

        self.urls.append(
            path(
                data_model.get_list_path(),
                self.views[list_view_name],
                name=list_view_name,
            )
        )

        # DetailView
        detail_view_class: ListView = type(  # type: ignore
            f"{module_camel_case}DetailView",
            (DataDetailView,),
            {"data_type": data_model},
        )
        detail_view_name = data_model.get_detail_path_name()

        self.views[detail_view_name] = detail_view_class.as_view()
        self.urls.append(
            path(
                data_model.get_detail_path(),
                self.views[detail_view_name],
                name=detail_view_name,
            )
        )


class FearConditioningDataListView(DataListView):
    data_type = FearConditioningData

    def get_queryset(self) -> QuerySet[BaseData]:
        return (
            super()
            .get_queryset()
            .order_by("participant_id", "module__sortorder", "trial")
        )


data_viewset_registry = DataViewsetRegistry()

data_viewset_registry.register(BasicInfoData)
data_viewset_registry.register(
    FearConditioningData, list_view_class=FearConditioningDataListView
)
