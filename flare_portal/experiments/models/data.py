from django.db import models

from .core import Nameable
from .modules import BaseModule


class BaseData(Nameable, models.Model):
    participant = models.ForeignKey(
        "experiments.Participant", on_delete=models.CASCADE, related_name="+"
    )
    module: BaseModule

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


class FearConditioningData(BaseData):
    module = models.ForeignKey(  # type: ignore
        "experiments.FearConditioningModule",
        on_delete=models.PROTECT,
        related_name="data",
    )
    trial = models.PositiveIntegerField()
    rating = models.PositiveIntegerField()
    conditional_stimulus = models.CharField(max_length=24)
    unconditional_stimulus = models.BooleanField()
    trial_started_at = models.DateTimeField()
    response_recorded_at = models.DateTimeField()
    volume_level = models.PositiveIntegerField()
    headphones = models.BooleanField()

    def __str__(self) -> str:
        return f"Participant: {self.participant_id} - Module: {self.module_id}"
