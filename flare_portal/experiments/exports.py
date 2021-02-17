import csv
import io
import zipfile
from datetime import datetime
from typing import IO, List, Type

from django.db.models import QuerySet
from django.utils import timezone

from rest_framework import serializers

from .models import (
    AffectiveRatingData,
    BasicInfoData,
    ContingencyAwarenessData,
    CriterionData,
    Experiment,
    FearConditioningData,
    Participant,
    PostExperimentQuestionsData,
    USUnpleasantnessData,
    VolumeCalibrationData,
)


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
        return f"{self.experiment.code}-{now}.csv"

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


class DataExporter(Exporter):
    def get_filename(self, current_time: datetime) -> str:
        now = current_time.strftime("%Y%m%dT%H%M%SZ")
        return (
            f"{self.experiment.code}-{now}-"
            f"{self.serializer_class.Meta.model.get_module_slug()}.csv"
        )


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


class FearConditioningDataExporter(DataExporter):
    serializer_class = FearConditioningDataSerializer

    def get_queryset(self) -> QuerySet[FearConditioningData]:
        return (
            FearConditioningData.objects.filter(module__experiment=self.experiment)
            .select_related("participant", "module", "module__experiment")
            .order_by("participant_id", "module__sortorder", "trial")
        )


class AffectiveRatingDataSerializer(DataSerializer):
    class Meta:
        model = AffectiveRatingData
        fields = DataSerializer.Meta.fields + ["stimulus", "rating"]


class AffectiveRatingDataExporter(DataExporter):
    serializer_class = AffectiveRatingDataSerializer

    def get_queryset(self) -> QuerySet[AffectiveRatingData]:
        return (
            AffectiveRatingData.objects.filter(module__experiment=self.experiment)
            .select_related("participant", "module")
            .order_by("participant_id", "module__sortorder")
        )


class BasicInfoDataSerializer(DataSerializer):
    class Meta:
        model = BasicInfoData
        fields = DataSerializer.Meta.fields + [
            "date_of_birth",
            "gender",
            "headphone_type",
            "device_make",
            "device_model",
            "os_name",
            "os_version",
        ]


class BasicInfoDataExporter(DataExporter):
    serializer_class = BasicInfoDataSerializer

    def get_queryset(self) -> QuerySet[BasicInfoData]:
        return (
            BasicInfoData.objects.filter(module__experiment=self.experiment)
            .select_related("participant", "module")
            .order_by("participant_id", "module__sortorder")
        )


class ContingencyAwarenessDataSerializer(DataSerializer):
    class Meta:
        model = ContingencyAwarenessData
        fields = DataSerializer.Meta.fields + [
            "awareness_answer",
            "confirmation_answer",
            "is_aware",
        ]


class ContingencyAwarenessDataExporter(DataExporter):
    serializer_class = ContingencyAwarenessDataSerializer

    def get_queryset(self) -> QuerySet[ContingencyAwarenessData]:
        return (
            ContingencyAwarenessData.objects.filter(module__experiment=self.experiment)
            .select_related("participant", "module")
            .order_by("participant_id", "module__sortorder")
        )


class CriterionDataSerializer(DataSerializer):
    question_id = serializers.CharField(source="question.pk")
    question = serializers.CharField(source="question.question_text")
    required_answer = serializers.CharField(source="question.required_answer")
    required = serializers.CharField(source="question.required")

    class Meta:
        model = CriterionData
        fields = DataSerializer.Meta.fields + [
            "question_id",
            "question",
            "required_answer",
            "required",
            "answer",
        ]


class CriterionDataExporter(DataExporter):
    serializer_class = CriterionDataSerializer

    def get_queryset(self) -> QuerySet[CriterionData]:
        return (
            CriterionData.objects.filter(module__experiment=self.experiment)
            .select_related("participant", "module", "question")
            .order_by("participant_id", "module__sortorder", "question_id")
        )


class VolumeCalibrationDataSerializer(DataSerializer):
    class Meta:
        model = VolumeCalibrationData
        fields = DataSerializer.Meta.fields + ["calibrated_volume_level", "rating"]


class VolumeCalibrationDataExporter(DataExporter):
    serializer_class = VolumeCalibrationDataSerializer

    def get_queryset(self) -> QuerySet[VolumeCalibrationData]:
        return (
            VolumeCalibrationData.objects.filter(module__experiment=self.experiment)
            .select_related("participant", "module")
            .order_by("participant_id", "module__sortorder")
        )


class PostExperimentQuestionsDataSerializer(DataSerializer):
    class Meta:
        model = PostExperimentQuestionsData
        fields = DataSerializer.Meta.fields + PostExperimentQuestionsData.fields


class PostExperimentQuestionsDataExporter(DataExporter):
    serializer_class = PostExperimentQuestionsDataSerializer

    def get_queryset(self) -> QuerySet[PostExperimentQuestionsData]:
        return (
            PostExperimentQuestionsData.objects.filter(
                module__experiment=self.experiment
            )
            .select_related("participant", "module")
            .order_by("participant_id", "module__sortorder")
        )


class USUnpleasantnessDataSerializer(DataSerializer):
    class Meta:
        model = USUnpleasantnessData
        fields = DataSerializer.Meta.fields + [
            "rating",
        ]


class USUnpleasantnessDataExporter(DataExporter):
    serializer_class = USUnpleasantnessDataSerializer

    def get_queryset(self) -> QuerySet[USUnpleasantnessData]:
        return (
            USUnpleasantnessData.objects.filter(module__experiment=self.experiment)
            .select_related("participant", "module")
            .order_by("participant_id", "module__sortorder")
        )


class ParticipantSerializer(serializers.ModelSerializer):
    experiment_code = serializers.CharField(source="experiment.code")
    voucher = serializers.CharField(source="get_voucher_display")

    class Meta:
        model = Participant
        fields = [
            "experiment_id",
            "experiment_code",
            "participant_id",
            "created_at",
            "started_at",
            "finished_at",
            "agreed_to_terms_and_conditions",
            "voucher",
            "rejection_reason",
            "current_module",
            "current_trial_index",
        ]


class ParticipantExporter(Exporter):
    serializer_class = ParticipantSerializer

    def get_filename(self, current_time: datetime) -> str:
        now = current_time.strftime("%Y%m%dT%H%M%SZ")
        return f"{self.experiment.code}-{now}-participants.csv"

    def get_queryset(self) -> QuerySet[Participant]:
        return Participant.objects.filter(experiment=self.experiment).order_by("pk")


class ZipExporter:
    exporters: List[Type[Exporter]] = [
        AffectiveRatingDataExporter,
        BasicInfoDataExporter,
        FearConditioningDataExporter,
        CriterionDataExporter,
        ContingencyAwarenessDataExporter,
        VolumeCalibrationDataExporter,
        ParticipantExporter,
        PostExperimentQuestionsDataExporter,
        USUnpleasantnessDataExporter,
        VolumeCalibrationDataExporter,
    ]

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
