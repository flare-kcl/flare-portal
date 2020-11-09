from typing import Any, Callable, Dict, List, Type

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import URLPattern, path, reverse
from django.utils.text import camel_case_to_spaces
from django.views.generic.edit import CreateView

from .models import BaseModule, Experiment


class ModuleFormViewMixin:
    template_name = "experiments/module_form.html"

    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        self.experiment = get_object_or_404(Experiment, pk=kwargs["experiment_pk"])
        return super().dispatch(*args, **kwargs)  # type: ignore

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)  # type: ignore
        context["experiment"] = self.experiment
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
        self.urls: List[URLPattern] = []
        self.views: Dict[str, Callable] = {}

    def register(self, module_model: Type[BaseModule]) -> None:
        """
        Dynamically creates views for a module
        """
        module_name = module_model.__name__.strip("Module")
        module_underscores = camel_case_to_spaces(module_name).replace(" ", "_")
        module_slug = module_underscores.replace("_", "-")

        # Create the module's CreateView
        create_view_class: CreateView = type(  # type: ignore
            f"{module_name}CreateView",
            (ModuleFormViewMixin, CreateView,),
            {
                "fields": ["experiment"]
                + [f.name for f in module_model._meta.fields if f.name != "sortorder"],
                "model": module_model,
            },
        )
        create_view_name = f"{module_underscores}_create"

        self.views[create_view_name] = create_view_class.as_view()
        self.urls.append(
            path(
                "projects/<int:project_pk>/experiments/<int:experiment_pk>/modules/"
                f"{module_slug}/add/",
                self.views[create_view_name],
                name=create_view_name,
            )
        )
