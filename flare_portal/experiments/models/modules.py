import re
from typing import List

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import pluralize
from django.utils.text import get_text_list

from extra_views import InlineFormSetFactory
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

    inlines: List[InlineFormSetFactory] = []

    class Meta:
        ordering = ["sortorder"]

    @classmethod
    def get_module_camel_case(cls) -> str:
        return re.sub("Module$", "", cls.__name__)

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


class BasicInfoModule(BaseModule):
    collect_date_of_birth = models.BooleanField(default=False)
    collect_gender = models.BooleanField(default=False)
    collect_headphone_make = models.BooleanField(default=False)
    collect_headphone_model = models.BooleanField(default=False)
    collect_headphone_label = models.BooleanField(default=False)

    def get_module_config(self) -> constants.ModuleConfigType:
        return constants.ModuleConfigType(
            id=self.pk,
            type=self.get_module_tag(),
            config={
                "collect_date_of_birth": self.collect_date_of_birth,
                "collect_gender": self.collect_gender,
                "collect_headphone_make": self.collect_headphone_make,
                "collect_headphone_model": self.collect_headphone_model,
                "collect_headphone_label": self.collect_headphone_label,
            },
        )

    def get_module_description(self) -> str:
        collecting = {
            "date of birth": self.collect_date_of_birth,
            "gender": self.collect_gender,
            "headphone type": True,
            "headphone make": self.collect_headphone_make,
            "headphone model": self.collect_headphone_model,
            "headphone label": self.collect_headphone_label,
            "device make and model": True,
            "OS name and version": True,
        }
        text = get_text_list([key for key, value in collecting.items() if value], "and")
        return "Collecting " + text

    def __str__(self) -> str:
        return "Basic info - " + super().__str__()


class CriterionQuestion(models.Model):
    question_text = models.CharField(max_length=255)
    help_text = models.TextField(blank=True)
    required_answer = models.BooleanField(
        default=None,
        null=True,
        blank=True,
        choices=((None, "Yes or No"), (True, "Yes"), (False, "No"),),
    )
    required = models.BooleanField(default=True)

    module = models.ForeignKey(
        "experiments.CriterionModule",
        on_delete=models.CASCADE,
        related_name="questions",
    )
    sortorder = models.PositiveIntegerField(default=0)

    inline_label = "Questions"

    def __str__(self) -> str:
        return self.question_text


class CriterionQuestionInline(InlineFormSetFactory):
    model = CriterionQuestion
    fields = ["question_text", "help_text", "required_answer", "required", "sortorder"]
    factory_kwargs = {"widgets": {"sortorder": forms.HiddenInput}, "extra": 0}


class CriterionModule(BaseModule):
    intro_text = models.TextField(blank=True)

    inlines = [CriterionQuestionInline]

    def get_module_description(self) -> str:
        question_count = self.questions.count()
        return f"{question_count} question{pluralize(question_count)}"

    def __str__(self) -> str:
        return "Criterion - " + super().__str__()
