import csv
import io
import random
import string
from typing import Any, Dict, List, Tuple

from django import forms
from django.core.validators import FileExtensionValidator
from django.forms import inlineformset_factory

from .models import BreakEndModule, BreakStartModule, Experiment, Participant


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = [
            "name",
            "description",
            "code",
            "owner",
            "trial_length",
            "rating_delay",
            "iti_min_delay",
            "iti_max_delay",
            "rating_scale_anchor_label_left",
            "rating_scale_anchor_label_center",
            "rating_scale_anchor_label_right",
            "us",
            "csa",
            "csb",
            "context_a",
            "context_b",
            "context_c",
            "gsa",
            "gsb",
            "gsc",
            "gsd",
        ]


class ExperimentCreateForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ExperimentForm.Meta.fields + ["project"]
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

        # TODO: Handle participant ID collissions
        Participant.objects.bulk_create(
            Participant(
                participant_id=f"{experiment.code}.{generate_participant_id()}",
                experiment=experiment,
            )
            for n in range(self.cleaned_data["participant_count"])
        )


class ParticipantUploadForm(forms.Form):
    import_file = forms.FileField(
        validators=[FileExtensionValidator(["csv"])],
    )

    def clean(self) -> Dict[str, Any]:
        # Don't continue if no upload
        file = self.cleaned_data.get("import_file")
        if file is None:
            return self.cleaned_data

        # Open uploaded file
        data = io.StringIO(file.read().decode("utf-8"))
        upload = csv.DictReader(data)

        # Build a list of ID's
        pids = []
        for row in upload:
            if pid := row.get("pid"):
                if len(pid) <= 24 and pid not in pids:
                    pids.append(pid)
                else:
                    self.add_error(
                        "import_file",
                        "Participant ID's must be less than 25 characters.",
                    )

        # Validate and remove any ID's that already exist
        row_count = len(pids)
        existing_participants = Participant.objects.filter(participant_id__in=pids)
        for participant in existing_participants:
            pids.remove(participant.participant_id)

        # Update data object
        self.cleaned_data["pids"] = pids
        self.cleaned_data["row_count"] = row_count
        return self.cleaned_data

    def save(self, *, experiment: Experiment) -> Tuple[List[Participant], int]:
        """
        Accepts an upload .csv file and creates the corresponding Participants.
        """

        if not self.is_valid():
            raise ValueError("Form should be valid before calling .save()")

        # Bulk create Participants in list
        participants = Participant.objects.bulk_create(
            Participant(
                participant_id=pid,
                experiment=experiment,
            )
            for pid in self.cleaned_data["pids"]
        )

        # Return objects create and how many rows in file
        return participants, self.cleaned_data["row_count"]


ParticipantFormSet = inlineformset_factory(
    Experiment, Participant, fields=["participant_id"], extra=0
)


class BreakStartModuleForm(forms.ModelForm):
    class Meta:
        model = BreakStartModule
        fields = [
            "experiment",
            "label",
            "duration",
            "start_title",
            "start_body",
            "end_title",
            "end_body",
        ]
        widgets = {"experiment": forms.HiddenInput()}

    def save(self, commit: bool = True) -> BreakStartModule:
        # Automatically create a matching end module when the start module is
        # created
        module = super().save(commit=False)

        if commit:
            module.save()
            BreakEndModule.objects.create(
                start_module=module,
                experiment=module.experiment,
                sortorder=1,
            )
        else:
            module.end_module = BreakEndModule(
                start_module=module,
                experiment=module.experiment,
                sortorder=1,
            )

        return module
