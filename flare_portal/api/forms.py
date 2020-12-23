from django import forms
from django.utils import timezone
from rest_framework import serializers
from flare_portal.experiments.models import Participant


class ConfigurationForm(forms.Form):
    participant = forms.ModelChoiceField(
        queryset=Participant.objects.all(),
        to_field_name="participant_id",
        error_messages={
            "invalid_choice": "This participant identifier is "
            "not correct, please contact your research assistant."
        },
    )

    def save(self):
        # Flag the participant as started the experiment
        participant = self.cleaned_data.get("participant")
        if participant.started_at == None:
            participant.started_at = timezone.now()
            participant.save()

    def clean(self):
        # Checks if the participant has logged in before.
        participant = self.cleaned_data.get("participant")
        if participant and participant.started_at != None:
            raise serializers.ValidationError(
                {
                    "participant": "This participant has already started "
                    "the experiment."
                }
            )


class SubmissionForm(forms.Form):
    participant = forms.ModelChoiceField(
        queryset=Participant.objects.all(),
        to_field_name="participant_id",
        error_messages={"invalid_choice": "Invalid participant"},
    )

    def save(self) -> Participant:
        # Flag the participant as started the experiment
        participant = self.cleaned_data.get("participant")
        if participant.finished_at == None:
            participant.finished_at = timezone.now()
            participant.save()

        return participant

    def clean(self):
        # Checks if the participant has logged in before.
        participant = self.cleaned_data.get("participant")

        # Check the participant has started.
        if participant and participant.started_at == None:
            raise serializers.ValidationError(
                {"participant": "This participant has not started an experiment."}
            )

        # Check that the participant hasn't already been marked as finished.
        if participant and participant.finished_at != None:
            raise serializers.ValidationError(
                {
                    "participant": "This participant has already finished "
                    "the experiment"
                }
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
