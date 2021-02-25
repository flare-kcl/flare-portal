import csv
import io
import random
import string
from typing import Any, Dict, List, Tuple

from django import forms
from django.db.models import QuerySet
from django.core.validators import FileExtensionValidator
from django.forms import inlineformset_factory

from flare_portal.users.models import User

from .models import BreakEndModule, BreakStartModule, Experiment, Participant, Project


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = [
            "name",
            "description",
            "contact_email",
            "code",
            "owner",
            "trial_length",
            "rating_delay",
            "iti_min_delay",
            "iti_max_delay",
            "rating_scale_anchor_label_left",
            "rating_scale_anchor_label_center",
            "rating_scale_anchor_label_right",
            "voucher_pool",
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


class ParticipantDeleteForm(forms.Form):
    participant: Participant = None
    participant_id_confirm = forms.CharField(
        max_length=25, label="Confirm Participant ID"
    )

    def __init__(self, participant: Participant, *args: Any, **kwargs: Any) -> None:
        super(ParticipantDeleteForm, self).__init__(*args, **kwargs)
        self.participant = participant

    def clean(self) -> Dict[str, Any]:
        # Check field matches participant_id
        cleaned_data = super().clean()
        if cleaned_data["participant_id_confirm"] != self.participant.participant_id:
            self.add_error(
                "participant_id_confirm", "Input does not match Participant ID"
            )

        return cleaned_data

    def save(self) -> None:
        """
        Deletes a specific participant
        """

        if not self.is_valid():
            raise ValueError("Form should be valid before calling .save()")

        # Validation passes so delete Participant
        self.participant.delete()


class ParticipantBulkDeleteForm(forms.Form):
    experiment: Experiment
    participants: QuerySet[Participant]

    def __init__(
        self, experiment: Experiment, participants: Any, *args: Any, **kwargs: Any
    ) -> None:
        super(ParticipantBulkDeleteForm, self).__init__(*args, **kwargs)
        self.experiment = experiment
        self.participants = participants

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()

        for participant in self.participants:
            # Check all the participants are part of the same experiment
            if participant.experiment != self.experiment:
                self.add_error(
                    None,
                    f"Participant {participant.participant_id} does not belong "
                    "to experiment {self.experiment.name}",
                )

                return cleaned_data

            # Check participant hasn't been allocated voucher
            if getattr(participant, "voucher", None) is not None:
                self.add_error(
                    None,
                    f"Participant {participant.participant_id} can't be "
                    "deleted because they have a voucher dispersed.",
                )

                return cleaned_data

            # Check participant hasn't started experiment
            if participant.started_at is not None:
                self.add_error(
                    None,
                    f"Participant {participant.participant_id} can't be "
                    "deleted because they have already started the experiment.",
                )

                return cleaned_data

        return cleaned_data

    def save(self) -> None:
        # Delete all the selected participants
        self.participants.delete()


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


class ProjectResearcherAddForm(forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any):
        super(ProjectResearcherAddForm, self).__init__(*args, **kwargs)
        project = kwargs.get("instance")
        self.fields["researchers"] = forms.ModelMultipleChoiceField(
            queryset=User.objects.exclude(pk=project.owner.pk), required=True
        )

    class Meta:
        model = Project
        fields = ("researchers",)

    def save(self, commit: bool = True) -> Project:
        researchers = self.cleaned_data.get("researchers", [])
        for resercher in researchers:
            self.instance.researchers.add(resercher.pk)

        if commit:
            self.instance.save()

        return self.instance


class ProjectResearcherDeleteForm(forms.Form):
    researcher_confirm = forms.CharField(
        max_length=24, required=True, label="Confirm User ID"
    )

    def __init__(self, *args: Any, project: Project, researcher: User, **kwargs: Any):
        super(ProjectResearcherDeleteForm, self).__init__(*args, **kwargs)
        self.project = project
        self.researcher = researcher

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()

        # Check the input matches
        researcher_confirm = self.cleaned_data.get("researcher_confirm")
        if researcher_confirm != self.researcher.username:
            self.add_error("researcher_confirm", "Input does not match User ID")

        return cleaned_data

    def save(self) -> Project:
        # Remove user as researcher
        self.project.researchers.remove(self.researcher.pk)
        self.project.save()
        return self.project
