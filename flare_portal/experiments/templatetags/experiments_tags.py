from typing import Any, List, Type

from django import template
from django.template.context import RequestContext
from django.urls import reverse

from flare_portal.api.registry import data_api_registry

from ..models import BaseData, Experiment, Module
from ..registry import module_registry

register = template.Library()


@register.simple_tag
def get_module_types() -> List[Type[Module]]:
    return module_registry.modules


@register.simple_tag
def get_module_data_types() -> List[Type[BaseData]]:
    return data_api_registry.data_models


@register.simple_tag
def get_module_create_url(module_class: Type[Module], experiment: Experiment) -> str:
    create_path_name = module_class.get_create_path_name()
    return reverse(
        f"experiments:modules:{create_path_name}",
        kwargs={"project_pk": experiment.project_id, "experiment_pk": experiment.pk},
    )


@register.simple_tag
def get_module_update_url(module: Module) -> str:
    if isinstance(module, Module):
        update_path_name = module.get_update_path_name()
        return reverse(
            f"experiments:modules:{update_path_name}",
            kwargs={
                "project_pk": module.experiment.project_id,
                "experiment_pk": module.experiment.pk,
                "module_pk": module.pk,
            },
        )

    return ""


@register.simple_tag
def get_module_delete_url(module: Module) -> str:
    delete_path_name = module.get_delete_path_name()
    return reverse(
        f"experiments:modules:{delete_path_name}",
        kwargs={
            "project_pk": module.experiment.project_id,
            "experiment_pk": module.experiment.pk,
            "module_pk": module.pk,
        },
    )


@register.simple_tag(takes_context=True)
def get_data_list_url(context: RequestContext, data_type: Type[BaseData]) -> str:
    list_path_name = data_type.get_list_path_name()
    return reverse(
        f"experiments:data:{list_path_name}",
        kwargs={
            "project_pk": context["view"].kwargs["project_pk"],
            "experiment_pk": context["view"].kwargs["experiment_pk"],
        },
    )


@register.simple_tag
def get_data_detail_url(data: BaseData) -> str:
    detail_path_name = data.get_detail_path_name()
    return reverse(
        f"experiments:data:{detail_path_name}",
        kwargs={
            "project_pk": data.module.experiment.project_id,
            "experiment_pk": data.module.experiment_id,
            "data_pk": data.pk,
        },
    )


@register.filter
def is_boolean(value: Any) -> bool:
    return isinstance(value, bool)
