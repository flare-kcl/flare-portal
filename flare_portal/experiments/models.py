from django.contrib.auth import get_user_model
from django.core import validators
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
