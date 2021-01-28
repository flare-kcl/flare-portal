from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from flare_portal.experiments.models import Experiment
from flare_portal.site_config.models import SiteConfiguration

from . import constants
from .forms import (
    ConfigurationForm,
    SubmissionForm,
    TermsAndConditionsForm,
    VoucherForm,
)


class ConfigurationAPIView(APIView):
    def post(self, request: Request, format: str = None) -> Response:
        form = ConfigurationForm(request.data)

        if form.is_valid():
            config = SiteConfiguration.get_solo()
            experiment: Experiment = form.cleaned_data["participant"].experiment

            # Invalidate the current particpant ID
            form.save()

            return Response(
                constants.ConfigType(
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
                        us=experiment.us.url,
                        csa=experiment.csa.url,
                        csb=experiment.csb.url,
                        context_a=(
                            experiment.context_a.url if experiment.context_a else None
                        ),
                        context_b=(
                            experiment.context_b.url if experiment.context_b else None
                        ),
                        context_c=(
                            experiment.context_c.url if experiment.context_c else None
                        ),
                        gsa=experiment.gsa.url if experiment.gsa else None,
                        gsb=experiment.gsb.url if experiment.gsb else None,
                        gsc=experiment.gsc.url if experiment.gsc else None,
                        gsd=experiment.gsd.url if experiment.gsd else None,
                    ),
                    config=constants.SiteConfigurationType(
                        terms_and_conditions=config.terms_and_conditions,
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


configuration_api_view = ConfigurationAPIView.as_view()


class SubmissionAPIView(APIView):
    def post(self, request: Request, format: str = None) -> Response:
        form = SubmissionForm(request.data)

        if form.is_valid():
            form.save()
            participant = form.cleaned_data["participant"]

            return Response(
                constants.SubmissionType(
                    participant_started_at=participant.started_at,
                    participant_finished_at=participant.finished_at,
                )
            )

        raise serializers.ValidationError(form.errors)


submission_api_view = SubmissionAPIView.as_view()


class TermsAndConditionsAPIView(APIView):
    def post(self, request: Request, format: str = None) -> Response:
        form = TermsAndConditionsForm(request.data)

        if form.is_valid():
            participant = form.save()
            return Response(
                {
                    "participant": participant.participant_id,
                    "agreed_to_terms_and_conditions": (
                        participant.agreed_to_terms_and_conditions
                    ),
                }
            )

        raise serializers.ValidationError(form.errors)


terms_and_conditions_api_view = TermsAndConditionsAPIView.as_view()


class VoucherAPIView(APIView):
    def handle_exception(self, exc: APIException) -> Response:
        response = super().handle_exception(exc)
        response.data["status"] = "error"
        response.data["error_code"] = exc.get_codes()
        response.data["error_message"] = exc.detail
        del response.data["detail"]
        return response

    def post(self, request: Request, format: str = None) -> Response:
        form = VoucherForm(request.data)

        if form.is_valid():
            voucher = form.save()
            return Response(
                {
                    "status": "success",
                    "voucher": voucher.code,
                }
            )

        return Response({"status": "error"}, status=400)


voucher_api_view = VoucherAPIView.as_view()
