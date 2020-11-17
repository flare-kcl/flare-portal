from django.contrib.auth import get_user_model
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


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

    rating_scale_anchor_label_left = models.CharField(
        max_length=255, default="Certain no scream"
    )
    rating_scale_anchor_label_center = models.CharField(
        max_length=255, default="Uncertain"
    )
    rating_scale_anchor_label_right = models.CharField(
        max_length=255, default="Certain scream"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self) -> str:
        return reverse(
            "experiments:experiment_detail",
            kwargs={"project_pk": self.project_id, "experiment_pk": self.pk},
        )

    def clean(self) -> None:
        if self.rating_delay > self.trial_length:
            raise ValidationError(
                {"rating_delay": "Rating delay cannot be longer than the trial length."}
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
