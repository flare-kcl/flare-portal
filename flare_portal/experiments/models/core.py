from django.contrib.auth import get_user_model
from django.core import validators
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.text import camel_case_to_spaces, slugify


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


def experiment_assets_path(instance: "Experiment", filename: str) -> str:
    return f"experiment_assets/{instance.pk}/{filename}"


class Experiment(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
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
    agreed_to_terms_and_conditions = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    udpated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)

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
                return "Unable to disburse voucher."

        return ""

    def __str__(self) -> str:
        return self.participant_id


class Nameable:
    @classmethod
    def get_module_camel_case(cls) -> str:
        return cls.__name__

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
