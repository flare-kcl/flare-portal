from typing import Any, Dict

from django import forms
from django.utils import timezone

from rest_framework import serializers
from rest_framework.exceptions import APIException

from flare_portal.experiments.models import Participant
from flare_portal.reimbursement.models import Voucher, VoucherPool


class ConfigurationForm(forms.Form):
    participant = forms.ModelChoiceField(
        queryset=Participant.objects.all(),
        to_field_name="participant_id",
        error_messages={
            "invalid_choice": "This participant identifier is "
            "not correct, please contact your research assistant."
        },
    )

    def save(self) -> Participant:
        # Flag the participant as started the experiment
        participant = self.cleaned_data.get("participant")
        if participant.started_at is None:
            participant.started_at = timezone.now()
            participant.save()

        return participant

    def clean(self) -> Dict[str, Any]:
        # Checks if the participant has logged in before.
        cleaned_data = super().clean()
        participant = cleaned_data.get("participant")
        if participant is not None and participant.started_at is not None:
            raise serializers.ValidationError(
                {
                    "participant": "This participant has already started "
                    "the experiment."
                }
            )
        return cleaned_data


class SubmissionForm(forms.Form):
    participant = forms.ModelChoiceField(
        queryset=Participant.objects.all(),
        to_field_name="participant_id",
        error_messages={"invalid_choice": "Invalid participant"},
    )

    def save(self) -> Participant:
        # Flag the participant as started the experiment
        participant = self.cleaned_data.get("participant")
        if participant.finished_at is None:
            participant.finished_at = timezone.now()
            participant.save()

        return participant

    def clean(self) -> Dict[str, Any]:
        # Checks if the participant has logged in before.
        cleaned_data = super().clean()
        participant = cleaned_data.get("participant")

        # Check the participant has started.
        if participant is not None and participant.started_at is None:
            raise serializers.ValidationError(
                {"participant": "This participant has not started an experiment."}
            )

        # Check that the participant hasn't already been marked as finished.
        if participant is not None and participant.finished_at is not None:
            raise serializers.ValidationError(
                {
                    "participant": "This participant has already finished "
                    "the experiment"
                }
            )

        return cleaned_data


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


class VoucherPoolEmpty(APIException):
    status_code = 200
    default_detail = ""  # Detail is taken from VoucherPool.empty_pool_message
    default_code = "pool_empty"


class VoucherPoolUnassigned(APIException):
    status_code = 400
    default_detail = "This experiment is not assigned a voucher pool"
    default_code = "pool_unassigned"


class VoucherForm(forms.Form):
    participant = forms.ModelChoiceField(
        queryset=Participant.objects.all(),
        to_field_name="participant_id",
    )

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()

        if participant := cleaned_data.get("participant"):
            if participant.started_at is None:
                self.add_error(
                    "participant", "Participant has not yet started the experiment."
                )

            if participant.finished_at is None:
                self.add_error(
                    "participant", "Participant has not yet finished the experiment."
                )

            if hasattr(participant, "voucher"):
                self.add_error(
                    "participant", "Participant has already claimed voucher."
                )

        return cleaned_data

    def save(self) -> Voucher:
        if not self.is_valid():
            raise ValueError("Form should be valid before calling .save()")

        participant = self.cleaned_data["participant"]
        try:
            pool = VoucherPool.objects.get(experiments=participant.experiment_id)
        except VoucherPool.DoesNotExist:
            raise VoucherPoolUnassigned()
        voucher = pool.vouchers.filter(participant__isnull=True).first()

        if voucher:
            voucher.participant = participant
            voucher.save()
        else:
            raise VoucherPoolEmpty(detail=pool.empty_pool_message)

        return voucher
