from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models
from django.urls import reverse

from model_utils import Choices
from model_utils.managers import InheritanceManager

from . import constants


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self) -> str:
        return reverse("experiments:experiment_list", kwargs={"project_pk": self.pk})

    def __str__(self) -> str:
        return self.name


class Experiment(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    code = models.CharField(
        max_length=6, unique=True, validators=[validators.RegexValidator(r"^[\w]+\Z")]
    )
    owner = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    project = models.ForeignKey("experiments.Project", on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self) -> str:
        return reverse(
            "experiments:experiment_detail",
            kwargs={"project_pk": self.project_id, "experiment_pk": self.pk},
        )

    def __str__(self) -> str:
        return self.name


class Participant(models.Model):
    participant_id = models.CharField(max_length=24, unique=True)
    experiment = models.ForeignKey(
        "experiments.Experiment", on_delete=models.CASCADE, related_name="participants"
    )

    def __str__(self) -> str:
        return self.participant_id


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
