from datetime import datetime
from typing import Any, Dict

from django import forms

from flare_portal.users.models import User

from .models import SiteConfiguration


class MarkdownWidget(forms.TextInput):
    template_name = "site_config/widgets/markdown.html"


class SiteConfigurationUpdateForm(forms.ModelForm):
    participant_terms_and_conditions = forms.CharField(
        widget=MarkdownWidget, label="Terms & Conditions", required=False
    )
    participant_privacy_policy = forms.CharField(
        widget=MarkdownWidget, label="Privacy Policy", required=False
    )

    researcher_terms_and_conditions = forms.CharField(
        widget=MarkdownWidget, label="Terms & Conditions", required=False
    )
    researcher_privacy_policy = forms.CharField(
        widget=MarkdownWidget, label="Privacy Policy", required=False
    )

    class Meta:
        model = SiteConfiguration
        exclude = ["researcher_terms_updated_at", "admin_contact_email"]

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        config = self.instance

        # If researcher terms changed then update timestamp
        if (
            config.researcher_terms_and_conditions
            != self.cleaned_data["researcher_terms_and_conditions"]
        ):
            cleaned_data["researcher_terms_updated_at"] = datetime.now()
        else:
            cleaned_data[
                "researcher_terms_updated_at"
            ] = config.researcher_terms_updated_at

        return cleaned_data

    def save(self, commit: bool = True) -> SiteConfiguration:
        config = self.instance

        # Update fields
        config.participant_terms_and_conditions = self.cleaned_data[
            "participant_terms_and_conditions"
        ]
        config.participant_privacy_policy = self.cleaned_data[
            "participant_privacy_policy"
        ]
        config.researcher_terms_and_conditions = self.cleaned_data[
            "researcher_terms_and_conditions"
        ]
        config.researcher_privacy_policy = self.cleaned_data[
            "researcher_privacy_policy"
        ]
        config.researcher_terms_updated_at = self.cleaned_data[
            "researcher_terms_updated_at"
        ]

        if commit:
            config.save()

        return config


class ResearcherTermsAgreeForm(forms.Form):
    agree_to_terms = forms.BooleanField()

    def __init__(self, user: User, *args: Any, **kwargs: Any) -> None:
        super(ResearcherTermsAgreeForm, self).__init__(*args, **kwargs)
        self.user = user

    def save(self) -> None:
        if self.cleaned_data.get("agree_to_terms"):
            self.user.agreed_terms_at = datetime.now()
            self.user.save()
