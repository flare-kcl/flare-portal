import csv
from typing import TextIO, Type

from django.db.models import QuerySet

from rest_framework import serializers

from .models import Experiment, FearConditioningData


class DataSerializer(serializers.ModelSerializer):
    experiment_id = serializers.CharField(source="module.experiment_id")
    experiment_code = serializers.CharField(source="module.experiment.code")
    module_type = serializers.CharField(source="module.get_module_tag")
    module_id = serializers.CharField(source="module.pk")
    module_label = serializers.CharField(source="module.label")
    participant_id = serializers.CharField(source="participant.participant_id")


class Exporter:
    serializer_class: Type[serializers.Serializer]

    def __init__(self, experiment: Experiment):
        self.experiment = experiment

    def get_queryset(self) -> QuerySet:
        """Returns the queryset used for the export"""
        raise NotImplementedError()

    def write(self, file: TextIO) -> None:
        """Writes the CSV into the given file"""
        serializer = self.serializer_class(self.get_queryset(), many=True)

        writer = csv.DictWriter(file, self.serializer_class.Meta.fields)
        writer.writeheader()
        writer.writerows(serializer.data)


class FearConditioningDataSerializer(DataSerializer):
    phase = serializers.CharField(source="module.phase")

    class Meta:
        model = FearConditioningData
        fields = [
            "experiment_id",
            "experiment_code",
            "module_type",
            "module_id",
            "module_label",
            "participant_id",
            "phase",
            "trial",
            "rating",
            "conditional_stimulus",
            "unconditional_stimulus",
            "trial_started_at",
            "response_recorded_at",
            "volume_level",
            "calibrated_volume_level",
            "headphones",
        ]


class FearConditioningDataExporter(Exporter):
    serializer_class = FearConditioningDataSerializer

    def get_queryset(self) -> QuerySet[FearConditioningData]:
        return (
            FearConditioningData.objects.filter(module__experiment=self.experiment)
            .select_related("participant", "module", "module__experiment")
            .order_by("participant_id", "module__sortorder", "trial")
        )
