from typing import Callable, Dict, List, Type

from django.urls import URLPattern, path

from rest_framework import serializers
from rest_framework.generics import CreateAPIView

from flare_portal.experiments.models import BaseData, FearConditioningData, Participant


class DataSerializerMixin(serializers.ModelSerializer):
    participant = serializers.SlugRelatedField(
        slug_field="participant_id", queryset=Participant.objects.all()
    )

    def validate(self, data: Dict) -> Dict:
        if data["participant"].experiment_id != data["module"].experiment_id:
            raise serializers.ValidationError(
                {
                    "participant": "This participant is not part of the "
                    "module's experiment."
                }
            )
        return data


class DataRegistry:
    def __init__(self) -> None:
        self.data_models: List[Type[BaseData]] = []
        self.urls: List[URLPattern] = []
        self.views: Dict[str, Callable] = {}

    def register(self, data_class: Type[BaseData]) -> None:
        module_camel_case = data_class.get_module_camel_case()
        self.data_models.append(data_class)

        class Meta:
            model = data_class
            fields = "__all__"

        serializer_class = type(
            f"{module_camel_case}Serializer", (DataSerializerMixin,), {"Meta": Meta}
        )

        api_path = data_class.get_module_slug() + "/"
        api_view_name = data_class.get_module_snake_case()
        api_view_class: CreateAPIView = type(
            f"{module_camel_case}APIView",
            (CreateAPIView,),
            {"serializer_class": serializer_class},
        )
        self.views[api_view_name] = api_view_class.as_view()
        self.urls.append(path(api_path, self.views[api_view_name], name=api_view_name))


module_data_registry = DataRegistry()

module_data_registry.register(FearConditioningData)
