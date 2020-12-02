from typing import Any, List, Tuple, Union

from django.contrib.admin.utils import get_fields_from_path
from django.db import models

from .core import Nameable
from .modules import BaseModule


def get_field_value(instance: models.Model, field: str) -> Any:
    field_path = field.split("__")
    attr = instance
    for field_name in field_path:
        if get_display := getattr(attr, f"get_{field_name}_display", None):
            attr = get_display()
        else:
            attr = getattr(attr, field_name)
    return attr


class BaseData(Nameable, models.Model):
    participant = models.ForeignKey(
        "experiments.Participant", on_delete=models.CASCADE, related_name="+"
    )
    module: BaseModule

    fields: Union[str, List] = "__all__"

    class Meta:
        abstract = True

    @classmethod
    def get_list_path_name(cls) -> str:
        module_snake_case = cls.get_module_snake_case()
        return f"{module_snake_case}_list"

    @classmethod
    def get_list_path(cls) -> str:
        module_slug = cls.get_module_slug().strip("-data")
        return (
            "projects/<int:project_pk>/experiments/<int:experiment_pk>/data/"
            f"{module_slug}/"
        )

    @classmethod
    def get_detail_path_name(cls) -> str:
        module_snake_case = cls.get_module_snake_case()
        return f"{module_snake_case}_detail"

    @classmethod
    def get_detail_path(cls) -> str:
        module_slug = cls.get_module_slug().strip("-data")
        return (
            "projects/<int:project_pk>/experiments/<int:experiment_pk>/data/"
            f"{module_slug}/<int:data_pk>/"
        )

    def get_data_values(self) -> List[Tuple]:
        """Returns a list of tuples of fields and their values"""
        if self.fields == "__all__":
            return [
                (f.verbose_name, get_field_value(self, f.name))  # type: ignore
                for f in self._meta.get_fields()
                if f.name not in ["id", "participant", "module"]
            ]

        return [
            (
                get_fields_from_path(self._meta.model, fname)[-1].verbose_name,
                get_field_value(self, fname),
            )
            for fname in self.fields
        ]


class FearConditioningData(BaseData):
    module = models.ForeignKey(  # type: ignore
        "experiments.FearConditioningModule",
        on_delete=models.PROTECT,
        related_name="data",
    )
    trial = models.PositiveIntegerField()
    rating = models.PositiveIntegerField()
    conditional_stimulus = models.CharField(max_length=24, verbose_name="CS")
    unconditional_stimulus = models.BooleanField(verbose_name="US")
    trial_started_at = models.DateTimeField()
    response_recorded_at = models.DateTimeField()
    volume_level = models.PositiveIntegerField()
    headphones = models.BooleanField()

    fields = [
        "module__phase",
        "trial",
        "rating",
        "conditional_stimulus",
        "unconditional_stimulus",
        "trial_started_at",
        "response_recorded_at",
        "volume_level",
        "headphones",
    ]

    def __str__(self) -> str:
        return f"Participant: {self.participant_id} - Module: {self.module_id}"
