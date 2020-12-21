from django.db import models

from solo.models import SingletonModel


class SiteConfiguration(SingletonModel):
    terms_and_conditions = models.TextField(blank=True)

    def __str__(self) -> str:
        return "Site configuration"
