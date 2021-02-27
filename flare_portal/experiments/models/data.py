import re
from typing import Any, List, Literal, Tuple, Union

from django.contrib.admin.utils import get_fields_from_path
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db import models

from model_utils import Choices

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

    fields: Union[Literal["__all__"], List] = "__all__"
    list_display: List = ["participant"]

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return (
            f"Participant: {self.participant_id} - "  # type:ignore
            f"Module: {self.module_id}"
        )

    @classmethod
    def get_list_path_name(cls) -> str:
        module_snake_case = cls.get_module_snake_case()
        return f"{module_snake_case}_list"

    @classmethod
    def get_list_path(cls) -> str:
        module_slug = re.sub("-data$", "", cls.get_module_slug())
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
        module_slug = re.sub("-data$", "", cls.get_module_slug())
        return (
            "projects/<int:project_pk>/experiments/<int:experiment_pk>/data/"
            f"{module_slug}/<int:data_pk>/"
        )

    def get_field_values(self, field_names: List[str]) -> List[Tuple[str, Any]]:
        """Returns a tuple of field names and values for the given fields"""

        field_values = []

        for fname in field_names:
            try:
                field_values.append(
                    (
                        get_fields_from_path(self._meta.model, fname)[-1].verbose_name,
                        get_field_value(self, fname),
                    )
                )
            except FieldDoesNotExist:
                value = getattr(self, fname)

                if callable(value):
                    value = value()
                field_values.append((fname, value))

        return field_values

    def get_data_values(self) -> List[Tuple[str, Any]]:
        """Returns data for the data detail view"""
        if self.fields == "__all__":
            return self.get_field_values(
                [
                    f.name
                    for f in self._meta.get_fields()
                    if f.name not in ["id", "participant", "module"]
                ]
            )

        return self.get_field_values(self.fields)

    @classmethod
    def get_list_display_columns(cls) -> List[str]:
        """Returns the column names for this model for use in the table"""

        display_columns = []

        for fname in cls.list_display:
            try:
                field = get_fields_from_path(cls, fname)[-1]
                display_columns.append(field.verbose_name)
            except FieldDoesNotExist:
                # Field is property/method
                display_columns.append(fname.replace("_", " "))

        return display_columns

    def get_list_display_values(self) -> List[Tuple[str, Any]]:
        """Returns a single row of data for the data list view"""
        return self.get_field_values(self.list_display)


class FearConditioningData(BaseData):
    module = models.ForeignKey(  # type: ignore
        "experiments.FearConditioningModule",
        on_delete=models.PROTECT,
        related_name="data",
    )
    trial = models.PositiveIntegerField()
    trial_by_stimulus = models.PositiveIntegerField()
    rating = models.PositiveIntegerField(blank=True, null=True)
    stimulus = models.CharField(max_length=24)
    normalised_stimulus = models.CharField(max_length=3, blank=True)
    reinforced_stimulus = models.CharField(max_length=3, blank=True)
    unconditional_stimulus = models.BooleanField(verbose_name="US")
    trial_started_at = models.DateTimeField()
    response_recorded_at = models.DateTimeField(blank=True, null=True)
    volume_level = models.DecimalField(
        max_digits=3, decimal_places=2, verbose_name="device volume level"
    )
    calibrated_volume_level = models.DecimalField(max_digits=3, decimal_places=2)
    headphones = models.BooleanField(verbose_name="headphones connected")
    did_leave_iti = models.BooleanField(verbose_name="did leave ITI", default=False)
    did_leave_task = models.BooleanField(default=False)

    fields = [
        "module__phase",
        "trial",
        "rating",
        "trial_by_stimulus",
        "stimulus",
        "reinforced_stimulus",
        "normalised_stimulus",
        "unconditional_stimulus",
        "trial_started_at",
        "response_recorded_at",
        "volume_level",
        "calibrated_volume_level",
        "headphones",
        "did_leave_iti",
        "did_leave_task",
    ]
    list_display = [
        "participant",
        "module__phase",
        "trial",
        "stimulus",
        "unconditional_stimulus",
        "rating",
    ]

    class Meta:
        # Each participant can only submit data once per trial
        unique_together = ("trial", "module", "participant")


class BasicInfoData(BaseData):
    # Note: When changing the gender options, also change the corresponding
    # list in the flare-app repo.
    GENDERS = Choices(
        ("male", "Male"),
        ("female", "Female"),
        ("non_binary", "Non-binary"),
        ("self_define", "Prefer to self-define"),
        ("dont_know", "Don't know"),
        ("no_answer", "Prefer not to answer"),
    )
    HEADPHONE_TYPES = Choices(
        ("in_ear", "In-ear"),
        ("on_ear", "On-ear"),
        ("over_ear", "Over-ear"),
    )

    module = models.ForeignKey(  # type: ignore
        "experiments.BasicInfoModule",
        on_delete=models.PROTECT,
        related_name="data",
    )

    # Optional
    date_of_birth = models.DateField(null=True)
    gender = models.CharField(
        max_length=24, choices=GENDERS, default=GENDERS.male, blank=True
    )
    headphone_make = models.CharField(max_length=255, blank=True)
    headphone_model = models.CharField(max_length=255, blank=True)
    headphone_label = models.CharField(max_length=255, blank=True)

    # Mandatory
    device_make = models.CharField(max_length=255)
    device_model = models.CharField(max_length=255)
    headphone_type = models.CharField(max_length=8, choices=HEADPHONE_TYPES)
    os_name = models.CharField(max_length=255)
    os_version = models.CharField(max_length=255)

    fields = [
        "date_of_birth",
        "gender",
        "headphone_type",
        "device_make",
        "device_model",
        "os_name",
        "os_version",
    ]
    list_display = [
        "participant",
        "date_of_birth",
        "gender",
        "headphone_type",
        "device_make",
        "os_name",
        "os_version",
    ]

    class Meta:
        # Each participant can only submit basic info once per module
        unique_together = ("participant", "module")

    def get_date_of_birth_display(self) -> str:
        if self.date_of_birth:
            return self.date_of_birth.strftime("%Y-%m")
        return ""


class CriterionData(BaseData):
    question = models.ForeignKey(
        "experiments.CriterionQuestion", on_delete=models.CASCADE
    )
    answer = models.BooleanField(null=True)

    module = models.ForeignKey(  # type: ignore
        "experiments.CriterionModule",
        on_delete=models.PROTECT,
        related_name="data",
    )

    list_display = [
        "participant",
        "question",
        "passed",
    ]

    class Meta:
        # Each participant can only answer a question once
        unique_together = ("participant", "question")

    def clean(self) -> None:
        if self.question.module != self.module:  # type: ignore
            raise ValidationError(
                {"question": "This question does not belong to that module."}
            )

    @property
    def passed(self) -> bool:
        """Whether or not the participant answered correctly for the question"""
        return (
            # No answer
            (self.answer is None and not self.question.required)
            # Correct answer
            or (
                self.question.required_answer is not None
                and self.question.required_answer == self.answer
            )
            # Either answer is correct as long as there is one
            or (self.question.required_answer is None and self.answer is not None)
            or False
        )


class VolumeCalibrationData(BaseData):
    calibrated_volume_level = models.DecimalField(max_digits=3, decimal_places=2)
    rating = models.PositiveIntegerField()

    module = models.ForeignKey(  # type: ignore
        "experiments.InstructionsModule",
        on_delete=models.PROTECT,
        related_name="data",
    )

    list_display = [
        "participant",
        "calibrated_volume_level",
        "rating",
    ]

    class Meta:
        # Each participant can only submit volume calibration data once per module
        unique_together = ("participant", "module")


class AffectiveRatingData(BaseData):
    stimulus = models.CharField(max_length=3)
    normalised_stimulus = models.CharField(max_length=3, blank=True)
    rating = models.PositiveIntegerField()
    module = models.ForeignKey(  # type: ignore
        "experiments.AffectiveRatingModule",
        on_delete=models.PROTECT,
        related_name="data",
    )

    list_display = [
        "participant",
        "stimulus",
        "normalised_stimulus",
        "rating",
    ]

    class Meta:
        # Data for this module can only be submitted once.
        unique_together = ("participant", "module", "stimulus")

    def clean(self) -> None:
        if self.rating < 0 or self.rating > 10:
            raise ValidationError("The rating must be between int between 0 & 10")


class PostExperimentQuestionsData(BaseData):
    experiment_unpleasant_rating = models.PositiveIntegerField()
    did_follow_instructions = models.BooleanField(null=True)
    did_remove_headphones = models.BooleanField(null=True)
    headphones_removal_point = models.CharField(max_length=255, null=True)
    did_pay_attention = models.BooleanField(null=True)
    task_environment = models.CharField(max_length=255, null=True)
    was_quiet = models.BooleanField(null=True)
    was_alone = models.BooleanField(null=True)
    was_interrupted = models.BooleanField(null=True)
    module = models.ForeignKey(  # type: ignore
        "experiments.PostExperimentQuestionsModule",
        on_delete=models.PROTECT,
        related_name="data",
    )

    class Meta:
        # Data for this module can only be submitted once.
        unique_together = ("participant", "module")

    list_display = [
        "experiment_unpleasant_rating",
        "did_follow_instructions",
        "did_remove_headphones",
        "did_pay_attention",
        "was_interrupted",
    ]

    fields = [
        "experiment_unpleasant_rating",
        "did_follow_instructions",
        "did_remove_headphones",
        "headphones_removal_point",
        "did_pay_attention",
        "task_environment",
        "was_quiet",
        "was_alone",
        "was_interrupted",
    ]


class USUnpleasantnessData(BaseData):
    rating = models.PositiveIntegerField()
    module = models.ForeignKey(  # type: ignore
        "experiments.USUnpleasantnessModule",
        on_delete=models.PROTECT,
        related_name="data",
    )

    class Meta:
        # Data for this module can only be submitted once.
        unique_together = ("participant", "module")

    list_display = [
        "participant",
        "rating",
    ]

    @classmethod
    def get_module_name(cls) -> str:
        return "US unpleasantness data"


class ContingencyAwarenessData(BaseData):
    awareness_answer = models.BooleanField()
    confirmation_answer = models.CharField(max_length=3, null=True)
    is_aware = models.BooleanField()
    module = models.ForeignKey(  # type: ignore
        "experiments.ContingencyAwarenessModule",
        on_delete=models.PROTECT,
        related_name="data",
    )

    class Meta:
        # Data for this module can only be submitted once.
        unique_together = ("participant", "module")

    list_display = [
        "participant",
        "is_aware",
    ]

    fields = [
        "participant",
        "awareness_answer",
        "confirmation_answer",
        "is_aware",
    ]
