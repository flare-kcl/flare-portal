import csv
import io
from decimal import Decimal

from django.test import TestCase

from ..exports import FearConditioningDataExporter
from ..factories import (
    ExperimentFactory,
    FearConditioningDataFactory,
    FearConditioningModuleFactory,
    ParticipantFactory,
)


class ModuleExportTest(TestCase):
    def test_export_data(self) -> None:
        experiment = ExperimentFactory()
        module = FearConditioningModuleFactory(experiment=experiment)
        participant = ParticipantFactory(experiment=experiment)
        data = FearConditioningDataFactory.create_batch(
            10,
            participant=participant,
            module=module,
            volume_level=Decimal("4.20"),
            calibrated_volume_level=Decimal("4.20"),
        )

        # Export the csv
        csv_export = io.StringIO()
        exporter = FearConditioningDataExporter(experiment)
        exporter.write(csv_export)

        # Check the data
        csv_export.seek(0)
        reader = csv.DictReader(csv_export)
        rows = [row for row in reader]

        self.assertEqual(len(rows), len(data))

        for row, fc_data in zip(rows, data):
            self.assertEqual(row["experiment_id"], str(fc_data.module.experiment.pk))
            self.assertEqual(row["experiment_code"], fc_data.module.experiment.code)
            self.assertEqual(row["module_type"], fc_data.module.get_module_tag())
            self.assertEqual(row["module_id"], str(fc_data.module.pk))
            self.assertEqual(row["module_label"], fc_data.module.label or "NA")
            self.assertEqual(row["participant_id"], fc_data.participant.participant_id)
            self.assertEqual(row["phase"], fc_data.module.phase)
            self.assertEqual(row["trial"], str(fc_data.trial))
            self.assertEqual(row["rating"], str(fc_data.rating))
            self.assertEqual(row["stimulus"], fc_data.stimulus)
            self.assertEqual(
                row["unconditional_stimulus"], str(fc_data.unconditional_stimulus)
            )
            self.assertEqual(
                row["trial_started_at"],
                fc_data.trial_started_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            )

            self.assertEqual(
                row["response_recorded_at"],
                fc_data.response_recorded_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            )
            self.assertEqual(row["volume_level"], str(fc_data.volume_level))
            self.assertEqual(
                row["calibrated_volume_level"], str(fc_data.calibrated_volume_level)
            )
            self.assertEqual(row["headphones"], str(fc_data.headphones))
