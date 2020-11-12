from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from . import constants
from .forms import ConfigurationForm


class ConfigurationAPIView(APIView):
    def post(self, request: Request, format: str = None) -> Response:
        form = ConfigurationForm(request.data)

        if form.is_valid():
            experiment = form.cleaned_data["participant"].experiment
            return Response(
                constants.ConfigType(
                    experiment=constants.ExperimentType(
                        id=experiment.pk, name=experiment.name,
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
