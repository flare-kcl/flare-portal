from django.utils import timezone
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from flare_portal.experiments.models import Experiment

from . import constants
from .forms import ConfigurationForm


class ConfigurationAPIView(APIView):
    def post(self, request: Request, format: str = None) -> Response:
        form = ConfigurationForm(request.data)

        if form.is_valid():
            participant = form.cleaned_data["participant"]
            experiment: Experiment = participant.experiment

            # Mark that the participant has started the experiment
            participant_started_at = participant.started_at
            if participant.started_at == None:
                participant.started_at = timezone.now()
                participant.save()

            return Response(
                constants.ConfigType(
                    participant_started_at=participant_started_at,
                    participant_finished_at=participant.finished_at,
                    experiment=constants.ExperimentType(
                        id=experiment.pk,
                        name=experiment.name,
                        description=experiment.description,
                        trial_length=experiment.trial_length,
                        rating_delay=experiment.rating_delay,
                        iti_min_delay=experiment.iti_min_delay,
                        iti_max_delay=experiment.iti_max_delay,
                        rating_scale_anchor_label_left=(
                            experiment.rating_scale_anchor_label_left
                        ),
                        rating_scale_anchor_label_center=(
                            experiment.rating_scale_anchor_label_center
                        ),
                        rating_scale_anchor_label_right=(
                            experiment.rating_scale_anchor_label_right
                        ),
                    ),
                    modules=[
                        module.get_module_config()
                        for module in (
                            experiment.modules.select_subclasses()  # type: ignore
                        )
                    ],
                )
            )

        raise serializers.ValidationError(form.errors)


class SubmissionAPIView(APIView):
    def post(self, request: Request, format: str = None) -> Response:
        form = ConfigurationForm(request.data)

        if form.is_valid():
            participant = form.cleaned_data["participant"]

            # Raise error if participant hasn't started
            if participant.started_at == None:
                raise serializers.ValidationError(
                    {"participant": "This participant has not started an experiment."}
                )

            # Mark participant as finished the experiment
            if participant.finished_at == None:
                participant.finished_at = timezone.now()
                participant.save()

            return Response(
                constants.SubmissionType(
                    participant_started_at=participant.started_at,
                    participant_finished_at=participant.finished_at,
                )
            )


submission_api_view = SubmissionAPIView.as_view()
configuration_api_view = ConfigurationAPIView.as_view()
