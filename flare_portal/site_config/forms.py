from typing import List
from django import forms

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
        exclude: List[str] = []

    def save(self, commit: bool = True) -> SiteConfiguration:
        config = self.instance
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
            "researcher_terms_and_conditions"
        ]

        if commit:
            config.save()

        return config
