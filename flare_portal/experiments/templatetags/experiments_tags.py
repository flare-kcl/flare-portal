from typing import List, Type

from django import template
from django.urls import reverse

from ..models import BaseModule, Experiment
from ..urls import registry

register = template.Library()


@register.simple_tag
def get_module_types() -> List[Type[BaseModule]]:
    return registry.modules


@register.simple_tag
def get_module_create_url(
    module_class: Type[BaseModule], experiment: Experiment
) -> str:
    create_path_name = module_class.get_create_path_name()
    return reverse(
        f"experiments:modules:{create_path_name}",
        kwargs={"project_pk": experiment.project_id, "experiment_pk": experiment.pk},
    )


@register.simple_tag
def get_module_update_url(module: BaseModule) -> str:
    update_path_name = module.get_update_path_name()
    return reverse(
        f"experiments:modules:{update_path_name}",
        kwargs={
            "project_pk": module.experiment.project_id,
            "experiment_pk": module.experiment.pk,
            "module_pk": module.pk,
        },
    )


@register.simple_tag
def get_module_delete_url(module: BaseModule) -> str:
    delete_path_name = module.get_delete_path_name()
    return reverse(
        f"experiments:modules:{delete_path_name}",
        kwargs={
            "project_pk": module.experiment.project_id,
            "experiment_pk": module.experiment.pk,
            "module_pk": module.pk,
        },
    )
