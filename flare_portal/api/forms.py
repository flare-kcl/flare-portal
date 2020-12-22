from django import forms

from flare_portal.experiments.models import Participant


class ConfigurationForm(forms.Form):
    participant = forms.ModelChoiceField(
        queryset=Participant.objects.all(),
        to_field_name="participant_id",
        error_messages={"invalid_choice": "Invalid participant"},
    )


class TermsAndConditionsForm(forms.Form):
    participant = forms.ModelChoiceField(
        queryset=Participant.objects.all(),
        to_field_name="participant_id",
        error_messages={"invalid_choice": "Invalid participant"},
    )

    def save(self) -> Participant:
        participant = self.cleaned_data["participant"]
        participant.agreed_to_terms_and_conditions = True
        participant.save()
        return participant
