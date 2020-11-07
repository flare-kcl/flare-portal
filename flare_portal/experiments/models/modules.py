from django.db import models

from model_utils import Choices
from model_utils.managers import InheritanceManager

from .. import constants


class BaseModule(models.Model):
    experiment = models.ForeignKey(
        "experiments.Experiment", on_delete=models.CASCADE, related_name="modules"
    )
    sortorder = models.PositiveIntegerField(default=0)

    objects = InheritanceManager()

    class Meta:
        ordering = ["sortorder"]

    def get_module_config(self) -> constants.ModuleConfigType:
        raise NotImplementedError()

    def __str__(self) -> str:
        return f"PK: {self.pk} - Sort order: {self.sortorder}"


class FearConditioningModule(BaseModule):
    PHASES = Choices(
        ("habituation", "Habituation"),
        ("acquisition", "Acquisition"),
        ("generalisation", "Generalisation"),
        ("extinction", "Extinction"),
        ("return_of_fear", "Return of fear"),
    )
    phase = models.CharField(max_length=24, choices=PHASES, default=PHASES.habituation)
    trials_per_stimulus = models.PositiveIntegerField(default=0)
    reinforcement_rate = models.PositiveIntegerField(default=0)
    rating_delay = models.FloatField(default=1)

    def get_module_config(self) -> constants.ModuleConfigType:
        return constants.ModuleConfigType(
            id=self.pk,
            type="FEAR_CONDITIONING",
            config={
                "phase": self.phase,
                "trials_per_stimulus": self.trials_per_stimulus,
                "reinforcement_rate": self.reinforcement_rate,
                "rating_delay": self.rating_delay,
            },
        )

    def __str__(self) -> str:
        return "Fear conditioning - " + super().__str__()
