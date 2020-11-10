from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import camel_case_to_spaces, slugify

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

    @classmethod
    def get_module_camel_case(cls) -> str:
        return cls.__name__.strip("Module")

    @classmethod
    def get_module_name(cls) -> str:
        return camel_case_to_spaces(cls.get_module_camel_case())

    @classmethod
    def get_module_snake_case(cls) -> str:
        return cls.get_module_name().replace(" ", "_")

    @classmethod
    def get_module_tag(cls) -> str:
        return cls.get_module_snake_case().upper()

    @classmethod
    def get_module_slug(cls) -> str:
        return slugify(cls.get_module_name())

    @classmethod
    def get_create_path_name(cls) -> str:
        module_snake_case = cls.get_module_snake_case()
        return f"{module_snake_case}_create"

    @classmethod
    def get_create_path(cls) -> str:
        module_slug = cls.get_module_slug()
        return (
            "projects/<int:project_pk>/experiments/<int:experiment_pk>/modules/"
            f"{module_slug}/add/"
        )

    @classmethod
    def get_update_path_name(cls) -> str:
        module_snake_case = cls.get_module_snake_case()
        return f"{module_snake_case}_update"

    @classmethod
    def get_update_path(cls) -> str:
        module_slug = cls.get_module_slug()
        return (
            "projects/<int:project_pk>/experiments/<int:experiment_pk>/modules/"
            f"{module_slug}/<int:module_pk>/"
        )

    def get_module_config(self) -> constants.ModuleConfigType:
        raise NotImplementedError()

    def get_module_description(self) -> str:
        """Short description of module configuration"""
        return ""

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
            type=self.get_module_tag(),
            config={
                "phase": self.phase,
                "trials_per_stimulus": self.trials_per_stimulus,
                "reinforcement_rate": self.reinforcement_rate,
                "rating_delay": self.rating_delay,
            },
        )

    def get_module_description(self) -> str:
        details = [
            self.get_phase_display(),
            f"Trials per stimulus: {self.trials_per_stimulus}",
            f"Reinforcement rate: {self.reinforcement_rate}",
            f"Rating delay: {self.rating_delay}",
        ]
        return ", ".join(details)

    def clean(self) -> None:
        if self.reinforcement_rate > self.trials_per_stimulus:
            raise ValidationError(
                {
                    "reinforcement_rate": "Reinforcement rate cannot be greater than "
                    "the number of trials per stimulus."
                }
            )

    def __str__(self) -> str:
        return "Fear conditioning - " + super().__str__()
