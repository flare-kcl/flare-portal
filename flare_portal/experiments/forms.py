import random
import string

from django import forms

from .models import Experiment, Participant


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = [
            "name",
            "description",
            "code",
            "owner",
            "project",
            "trial_length",
            "rating_delay",
            "rating_scale_anchor_label_left",
            "rating_scale_anchor_label_center",
            "rating_scale_anchor_label_right",
        ]
        widgets = {"project": forms.HiddenInput()}


def generate_participant_id() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choice(alphabet) for i in range(6))


class ParticipantBatchForm(forms.Form):
    participant_count = forms.IntegerField(min_value=1)

    def save(self, *, experiment: Experiment) -> None:
        """
        Creates a batch of participants for an experiment
        """

        if not self.is_valid():
            raise ValueError("Form should be valid before calling .save()")

        Participant.objects.bulk_create(
            Participant(
                participant_id=f"{experiment.code}.{generate_participant_id()}",
                experiment=experiment,
            )
            for n in range(self.cleaned_data["participant_count"])
        )
