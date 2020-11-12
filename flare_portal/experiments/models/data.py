from django.db import models


class FearConditioningData(models.Model):
    participant = models.ForeignKey(
        "experiments.Participant", on_delete=models.CASCADE, related_name="+"
    )
    module = models.ForeignKey(
        "experiments.FearConditioningModule",
        on_delete=models.PROTECT,
        related_name="data",
    )
    trial = models.PositiveIntegerField()
    rating = models.PositiveIntegerField()
    conditional_stimulus = models.CharField(max_length=24)
    unconditional_stimulus = models.BooleanField()
    recorded_at = models.DateTimeField()
    volume_level = models.PositiveIntegerField()
    headphones = models.BooleanField()

    def __str__(self) -> str:
        return f"Participant: {self.participant_id} - Module: {self.module_id}"
