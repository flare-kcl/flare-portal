from django.db import models

from solo.models import SingletonModel


class SiteConfiguration(SingletonModel):
    admin_contact_email = models.EmailField(default="flare@kcl.ac.uk")
    participant_terms_and_conditions = models.TextField(
        default="# Terms and Conditions", blank=True
    )
    researcher_terms_and_conditions = models.TextField(
        default="# Terms and Conditions", blank=True
    )
    participant_privacy_policy = models.TextField(
        default="# Privacy Policy", blank=True
    )
    researcher_privacy_policy = models.TextField(default="# Privacy Policy", blank=True)
    researcher_terms_updated_at = models.DateTimeField(null=True)

    def __str__(self) -> str:
        return "Site configuration"
