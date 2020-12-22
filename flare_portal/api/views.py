from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from flare_portal.experiments.models import Experiment
from flare_portal.site_config.models import SiteConfiguration

from . import constants
from .forms import ConfigurationForm, TermsAndConditionsForm


class ConfigurationAPIView(APIView):
    def post(self, request: Request, format: str = None) -> Response:
        form = ConfigurationForm(request.data)

        if form.is_valid():
            experiment: Experiment = form.cleaned_data["participant"].experiment
            config = SiteConfiguration.get_solo()
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
