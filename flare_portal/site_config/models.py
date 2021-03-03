from django.db import models

from solo.models import SingletonModel


class SiteConfiguration(SingletonModel):
    participant_terms_and_conditions = models.TextField(blank=True)
    participant_privacy_policy = models.TextField(blank=True)
    researcher_terms_and_conditions = models.TextField(blank=True)
    researcher_privacy_policy = models.TextField(blank=True)

    def __str__(self) -> str:
        return "Site configuration"
