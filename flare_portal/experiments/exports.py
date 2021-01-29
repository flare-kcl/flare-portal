import csv
import io
import zipfile
from datetime import datetime
from typing import IO, Type

from django.db.models import QuerySet
from django.utils import timezone

from rest_framework import serializers

from .models import Experiment, FearConditioningData


class DataSerializer(serializers.ModelSerializer):
    experiment_id = serializers.CharField(source="module.experiment_id")
    experiment_code = serializers.CharField(source="module.experiment.code")
    module_type = serializers.CharField(source="module.get_module_tag")
    module_id = serializers.CharField(source="module.pk")
    module_label = serializers.CharField(source="module.label")
    participant_id = serializers.CharField(source="participant.participant_id")

    class Meta:
        fields = [
            "experiment_id",
            "experiment_code",
            "module_type",
            "participant_id",
            "module_id",
            "module_label",
        ]


class Exporter:
    serializer_class: Type[serializers.Serializer]

    def __init__(self, experiment: Experiment):
        self.experiment = experiment

    def get_filename(self, current_time: datetime) -> str:
        now = current_time.strftime("%Y%m%dT%H%M%SZ")
        return (
            f"{self.experiment.code}-{now}-"
            f"{self.serializer_class.Meta.model.get_module_slug()}.csv"
        )

    def get_queryset(self) -> QuerySet:
        """Returns the queryset used for the export"""
        raise NotImplementedError()

    def write(self, file: io.StringIO) -> None:
        """Writes the CSV into the given file"""
        serializer = self.serializer_class(self.get_queryset(), many=True)

        writer = csv.DictWriter(file, self.serializer_class.Meta.fields)
        writer.writeheader()
        writer.writerows(serializer.data)

        file.seek(0)


class FearConditioningDataSerializer(DataSerializer):
    phase = serializers.CharField(source="module.phase")

    class Meta:
        model = FearConditioningData
        fields = DataSerializer.Meta.fields + [
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


class ZipExport:
    exporters = [FearConditioningDataExporter]

    def __init__(self, experiment: Experiment):
        self.experiment = experiment

    def get_filename(self, current_time: datetime) -> str:
        now = current_time.strftime("%Y%m%dT%H%M%SZ")
        return f"{self.experiment.code}-{now}.zip"

    def write(self, content: IO) -> str:
        now = timezone.now()

        # Gather files
        files = []

        for exporter_class in self.exporters:
            csv_export = io.StringIO()
            exporter = exporter_class(self.experiment)
            exporter.write(csv_export)
            files.append((exporter.get_filename(now), csv_export))

        with zipfile.ZipFile(
            content, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as archive_file:
            for filename, file in files:
                archive_file.writestr(filename, file.read())

        return self.get_filename(now)
