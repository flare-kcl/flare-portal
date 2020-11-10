from typing import Any, Callable, Dict, List, Type

from django import forms
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import URLPattern, path, reverse
from django.views.generic.edit import CreateView, UpdateView

from .models import BaseModule, Experiment


class ModuleFormViewMixin:
    context_object_name = "module"
    template_name = "experiments/module_form.html"

    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        self.experiment = get_object_or_404(Experiment, pk=kwargs["experiment_pk"])
        return super().dispatch(*args, **kwargs)  # type: ignore

    def get_initial(self) -> dict:
        return {"experiment": self.experiment.pk}

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)  # type: ignore
        context["experiment"] = self.experiment

        if module_type := getattr(self, "model", None):
            context["module_type"] = module_type
        elif form_class := getattr(self, "form_class", None):
            context["module_type"] = form_class.Meta.model
        return context

    def get_success_url(self) -> str:
        return reverse(
            "experiments:experiment_detail",
            kwargs={
                "project_pk": self.experiment.project_id,
                "experiment_pk": self.experiment.pk,
            },
        )


class ModuleRegistry:
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
            (ModuleFormViewMixin, CreateView,),
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
            (ModuleFormViewMixin, UpdateView,),
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
