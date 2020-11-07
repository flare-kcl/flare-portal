from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from flare_portal.experiments.models import Experiment

from . import constants


class ConfigurationAPIView(APIView):
    def post(self, request: Request, format: str = None) -> Response:
        experiment = Experiment.objects.get()
        return Response(
            constants.ConfigType(
                experiment=constants.ExperimentType(
                    id=experiment.pk, name=experiment.name,
                ),
                modules=[
                    module.get_module_config()
                    for module in experiment.modules.select_subclasses()  # type: ignore
                ],
            )
        )


configuration_api_view = ConfigurationAPIView.as_view()
