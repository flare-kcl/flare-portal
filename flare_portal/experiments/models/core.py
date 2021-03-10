import string
from typing import Any, List, Tuple

from django.contrib.auth import get_user_model
from django.core import validators
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.text import camel_case_to_spaces, slugify


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    researchers = models.ManyToManyField(get_user_model(), related_name="projects")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self) -> str:
        return reverse("experiments:experiment_list", kwargs={"project_pk": self.pk})

    def __str__(self) -> str:
        return self.name

    def get_researchers(self) -> QuerySet[Any]:
        return (
            get_user_model().objects.filter(pk=self.owner.pk) | self.researchers.all()
        )


def experiment_assets_path(instance: "Experiment", filename: str) -> str:
    return f"experiment_assets/{instance.pk}/{filename}"


class Experiment(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    code = models.CharField(
        max_length=6,
        unique=True,
        validators=[
            validators.RegexValidator(
                r"^[\w]+\Z", message="Please only enter alphanumeric values."
            )
        ],
    )
    owner = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    project = models.ForeignKey("experiments.Project", on_delete=models.CASCADE)
    trial_length = models.FloatField()
    rating_delay = models.FloatField(default=1)
    minimum_volume = models.FloatField(
        default=1,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )
    iti_min_delay = models.PositiveIntegerField(default=1, verbose_name="ITI min delay")
    iti_max_delay = models.PositiveIntegerField(default=3, verbose_name="ITI max delay")

    rating_scale_anchor_label_left = models.CharField(
        max_length=255, default="Certain no scream"
    )
    rating_scale_anchor_label_center = models.CharField(
        max_length=255, default="Uncertain"
    )
    rating_scale_anchor_label_right = models.CharField(
        max_length=255, default="Certain scream"
    )

    voucher_pool = models.ForeignKey(
        "reimbursement.VoucherPool",
        on_delete=models.SET_NULL,
        related_name="experiments",
        blank=True,
        null=True,
    )

    # Assets
    us = models.FileField(
        upload_to=experiment_assets_path,
        verbose_name="US",
        validators=[FileExtensionValidator(["mp3", "wav"])],
    )
    csa = models.ImageField(
        upload_to=experiment_assets_path,
        verbose_name="CS A",
        validators=[FileExtensionValidator(["png"])],
    )
    csb = models.ImageField(
        upload_to=experiment_assets_path,
        verbose_name="CS B",
        validators=[FileExtensionValidator(["png"])],
    )
    context_a = models.ImageField(
        upload_to=experiment_assets_path,
        blank=True,
        verbose_name="context A",
        validators=[FileExtensionValidator(["png"])],
    )
    context_b = models.ImageField(
        upload_to=experiment_assets_path,
        blank=True,
        verbose_name="context B",
        validators=[FileExtensionValidator(["png"])],
    )
    context_c = models.ImageField(
        upload_to=experiment_assets_path,
        blank=True,
        verbose_name="context C",
        validators=[FileExtensionValidator(["png"])],
    )
    gsa = models.ImageField(
        upload_to=experiment_assets_path,
        blank=True,
        verbose_name="GS A",
        validators=[FileExtensionValidator(["png"])],
    )
    gsb = models.ImageField(
        upload_to=experiment_assets_path,
        blank=True,
        verbose_name="GS B",
        validators=[FileExtensionValidator(["png"])],
    )
    gsc = models.ImageField(
        upload_to=experiment_assets_path,
        blank=True,
        verbose_name="GS C",
        validators=[FileExtensionValidator(["png"])],
    )
    gsd = models.ImageField(
        upload_to=experiment_assets_path,
        blank=True,
        verbose_name="GS D",
        validators=[FileExtensionValidator(["png"])],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self) -> str:
        return reverse(
            "experiments:experiment_detail",
            kwargs={"project_pk": self.project_id, "experiment_pk": self.pk},
        )

    def clean(self) -> None:
        validation_errors = {}

        if self.rating_delay > self.trial_length:
            validation_errors[
                "rating_delay"
            ] = "Rating delay cannot be longer than the trial length."

        if self.iti_min_delay > self.iti_max_delay:
            validation_errors[
                "iti_min_delay"
            ] = "Minimum delay cannot be shorter than maximum delay."

        if validation_errors:
            raise ValidationError(validation_errors)

    def __str__(self) -> str:
        return self.name


class Participant(models.Model):
    participant_id = models.CharField(max_length=24, unique=True)
    experiment = models.ForeignKey(
        "experiments.Experiment", on_delete=models.CASCADE, related_name="participants"
    )

    current_module = models.ForeignKey(
        "experiments.BaseModule", on_delete=models.CASCADE, null=True
    )
    current_trial_index = models.PositiveIntegerField(null=True)
    agreed_to_terms_and_conditions = models.BooleanField(null=True)
    lock_reason = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    udpated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)

    @property
    def reinforced_stimulus(self) -> str:
        from flare_portal.experiments.models import FearConditioningData

        # Get the first trial response
        trial = FearConditioningData.objects.filter(participant_id=self.pk).first()
        if trial:
            return trial.reinforced_stimulus

        return ""

    def get_voucher_status(self) -> str:
        """Displays the voucher status"""
        if self.finished_at and self.experiment.voucher_pool_id:
            try:
                if str(self.voucher) is not None:
                    return "Allocated"
            except ObjectDoesNotExist:
                return "Failed"

        return ""

    def get_voucher_display(self) -> str:
        """Displays the voucher code

        This could also display a message telling the researcher that this
        participant should have gotten a voucher but didn't.

        When irrelevant, this displays an empty string
        """
        if self.finished_at and self.experiment.voucher_pool_id:
            try:
                return str(self.voucher)
            except ObjectDoesNotExist:
                return "Unable to allocate voucher."

        return ""

    def has_been_rejected(self) -> bool:
        """Has the participant been locked out by the app?"""
        return self.lock_reason != ""

    def get_data_values(self) -> List[Tuple[str, Any]]:
        """Returns data for the data detail view"""
        fields = [
            ("Experiment", self.experiment),
            (
                "Current Module",
                self.current_module.specific.get_module_title()
                if self.current_module
                else None,
            ),
            ("Current Trial Index", self.current_trial_index),
            ("Reinforced Stimulus", self.reinforced_stimulus),
            ("Agreed to T&C's", self.agreed_to_terms_and_conditions),
            ("Voucher Code", self.get_voucher_display()),
            ("Lock Reason", self.lock_reason),
            ("Last Updated", self.udpated_at),
            ("Started At", self.started_at),
            ("Finished At", self.finished_at),
        ]

        return fields

    def __str__(self) -> str:
        return self.participant_id


class Nameable:
    @classmethod
    def get_module_camel_case(cls) -> str:
        return cls.__name__

    @classmethod
    def get_base_name(cls) -> str:
        return camel_case_to_spaces(cls.get_module_camel_case())

    @classmethod
    def get_module_name(cls) -> str:
        return string.capwords(cls.get_base_name())

    @classmethod
    def get_module_snake_case(cls) -> str:
        return cls.get_base_name().replace(" ", "_")

    @classmethod
    def get_module_tag(cls) -> str:
        return cls.get_module_snake_case().upper()

    @classmethod
    def get_module_slug(cls) -> str:
        return slugify(cls.get_base_name())
