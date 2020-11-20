from django.db import models

from .core import Nameable


class BaseData(Nameable, models.Model):
    participant = models.ForeignKey(
        "experiments.Participant", on_delete=models.CASCADE, related_name="+"
    )

    class Meta:
        abstract = True


class FearConditioningData(BaseData):
    module = models.ForeignKey(
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
