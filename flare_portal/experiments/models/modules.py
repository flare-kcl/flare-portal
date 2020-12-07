from django.core.exceptions import ValidationError
from django.db import models

from model_utils import Choices
from model_utils.managers import InheritanceManager

from .. import constants
from .core import Nameable


class BaseModule(Nameable, models.Model):
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

    @classmethod
    def get_delete_path_name(cls) -> str:
        module_snake_case = cls.get_module_snake_case()
        return f"{module_snake_case}_delete"

    @classmethod
    def get_delete_path(cls) -> str:
        module_slug = cls.get_module_slug()
        return (
            "projects/<int:project_pk>/experiments/<int:experiment_pk>/modules/"
            f"{module_slug}/<int:module_pk>/delete/"
        )

    def get_module_config(self) -> constants.ModuleConfigType:
        raise NotImplementedError()

    def get_module_title(self) -> str:
        """Short title for this module"""
        return self.get_module_name()

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
    reinforcement_rate = models.PositiveIntegerField(
        default=0, verbose_name="Number of reinforced CS+ trials"
    )
    generalisation_stimuli_enabled = models.BooleanField(default=False)

    def get_module_config(self) -> constants.ModuleConfigType:
        return constants.ModuleConfigType(
            id=self.pk,
            type=self.get_module_tag(),
            config={
                "phase": self.phase,
                "trials_per_stimulus": self.trials_per_stimulus,
                "reinforcement_rate": self.reinforcement_rate,
                "generalisation_stimuli_enabled": self.generalisation_stimuli_enabled,
            },
        )

    def get_module_title(self) -> str:
        return self.get_phase_display()

    def get_module_description(self) -> str:
        details = [
            f"Trials per stimulus: {self.trials_per_stimulus}",
            f"Number of reinforced CS+ trials: {self.reinforcement_rate}",
            f"GS: {'Enabled' if self.generalisation_stimuli_enabled else 'Disabled'}",
        ]
        return ", ".join(details)

    def clean(self) -> None:
        if self.reinforcement_rate > self.trials_per_stimulus:
            raise ValidationError(
                {
                    "reinforcement_rate": "Number of reinforced CS+ trials "
                    "cannot be greater than the number of trials per stimulus."
                }
            )

    def __str__(self) -> str:
        return "Fear conditioning - " + super().__str__()
