from typing import Any, Callable, Dict, List, Type

from django import forms
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import URLPattern, path, reverse
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .models import BaseModule, Experiment


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
            (ModuleCreateViewMixin, CreateView,),
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
            (ModuleUpdateViewMixin, UpdateView,),
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
