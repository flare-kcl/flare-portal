from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils.dateparse import parse_datetime

from flare_portal.experiments.factories import (
    ExperimentFactory,
    FearConditioningModuleFactory,
    ParticipantFactory,
)
from flare_portal.experiments.models import (
    Experiment,
    FearConditioningModule,
    Participant,
)


class ConfigurationAPIViewTest(TestCase):
    def test_post(self) -> None:
        experiment: Experiment = ExperimentFactory()
        ParticipantFactory(participant_id="Flare.ABCDEF", experiment=experiment)

        module1: FearConditioningModule = FearConditioningModuleFactory(
            experiment=experiment, sortorder=1
        )

        module2: FearConditioningModule = FearConditioningModuleFactory(
            experiment=experiment, sortorder=2
        )

        resp = self.client.post(
            reverse("api:configuration"),
            {"participant": "Flare.ABCDEF"},
            content_type="application/json",
        )

        self.assertEqual(200, resp.status_code)

        data = resp.json()

        self.assertEqual(
            data["experiment"],
            {
                "id": experiment.pk,
                "name": experiment.name,
                "trial_length": experiment.trial_length,
                "rating_delay": experiment.rating_delay,
                "rating_scale_anchor_label_left": (
                    experiment.rating_scale_anchor_label_left
                ),
                "rating_scale_anchor_label_center": (
                    experiment.rating_scale_anchor_label_center
                ),
                "rating_scale_anchor_label_right": (
                    experiment.rating_scale_anchor_label_right
                ),
            },
        )
        self.assertEqual(
            data["modules"],
            [
                {
                    "id": module1.pk,
                    "type": "FEAR_CONDITIONING",
                    "config": {
                        "phase": module1.phase,
                        "trials_per_stimulus": module1.trials_per_stimulus,
                        "reinforcement_rate": module1.reinforcement_rate,
                        "generalisation_stimuli_enabled": (
                            module1.generalisation_stimuli_enabled
                        ),
                    },
                },
                {
                    "id": module2.pk,
                    "type": "FEAR_CONDITIONING",
                    "config": {
                        "phase": module2.phase,
                        "trials_per_stimulus": module2.trials_per_stimulus,
                        "reinforcement_rate": module2.reinforcement_rate,
                        "generalisation_stimuli_enabled": (
                            module2.generalisation_stimuli_enabled
                        ),
                    },
                },
            ],
        )

    def test_validation(self) -> None:
        resp = self.client.post(
            reverse("api:configuration"), {"participant": "Flare.ABCDEF"}
        )

        self.assertEqual(400, resp.status_code)

        self.assertEqual(resp.json(), {"participant": ["Invalid participant"]})


class ModuleDataAPIViewTest(TestCase):
    def test_post(self) -> None:
        experiment: Experiment = ExperimentFactory()
        module: FearConditioningModule = FearConditioningModuleFactory(
            experiment=experiment
        )
        participant: Participant = ParticipantFactory(experiment=experiment)

        url = reverse("api:fear_conditioning_data")

        json_data = {
            "participant": participant.participant_id,
            "module": module.pk,
            "trial": 1,
            "rating": 5,
            "conditional_stimulus": "CSA",
            "unconditional_stimulus": True,
            "trial_started_at": parse_datetime("2020-01-01T00:00Z"),
            "response_recorded_at": parse_datetime("2020-01-01T00:00Z"),
            "volume_level": "0.50",
            "headphones": True,
        }

        resp = self.client.post(url, json_data, content_type="application/json")

        self.assertEqual(201, resp.status_code)

        # Verify data posted
        data = module.data.get()

        response_data = {
            **resp.json(),
            "trial_started_at": parse_datetime(resp.json()["trial_started_at"]),
            "response_recorded_at": parse_datetime(resp.json()["response_recorded_at"]),
        }

        self.assertEqual(response_data, {**json_data, "id": data.pk})

        self.assertEqual(data.participant.participant_id, json_data["participant"])
        self.assertEqual(data.module_id, json_data["module"])
        self.assertEqual(data.trial, json_data["trial"])
        self.assertEqual(data.rating, json_data["rating"])
        self.assertEqual(data.conditional_stimulus, json_data["conditional_stimulus"])
        self.assertEqual(
            data.unconditional_stimulus, json_data["unconditional_stimulus"]
        )
        self.assertEqual(data.trial_started_at, json_data["trial_started_at"])
        self.assertEqual(data.response_recorded_at, json_data["response_recorded_at"])
        self.assertEqual(data.volume_level, Decimal(json_data["volume_level"]))
        self.assertEqual(data.headphones, json_data["headphones"])

    def test_validation(self) -> None:
        # Should not be able to add data for a participant that is not in the
        # same experiment as the module
        module: FearConditioningModule = FearConditioningModuleFactory()
        participant: Participant = ParticipantFactory()

        url = reverse("api:fear_conditioning_data")

        json_data = {
            "participant": participant.participant_id,
            "module": module.pk,
            "trial": 1,
            "rating": 5,
            "conditional_stimulus": "CSA",
            "unconditional_stimulus": True,
            "trial_started_at": parse_datetime("2020-01-01T00:00Z"),
            "response_recorded_at": parse_datetime("2020-01-01T00:00Z"),
            "volume_level": 0.50,
            "headphones": True,
        }

        resp = self.client.post(url, json_data, content_type="application/json")

        self.assertEqual(400, resp.status_code)

        self.assertEqual(
            resp.json(),
            {
                "participant": [
                    "This participant is not part of the module's experiment."
                ]
            },
        )


class FearConditioningDataAPIViewTest(TestCase):
    def test_unique_trial(self) -> None:
        experiment: Experiment = ExperimentFactory()
        module: FearConditioningModule = FearConditioningModuleFactory(
            experiment=experiment
        )
        participant: Participant = ParticipantFactory(experiment=experiment)

        url = reverse("api:fear_conditioning_data")

        json_data = {
            "participant": participant.participant_id,
            "module": module.pk,
            "trial": 1,
            "rating": 5,
            "conditional_stimulus": "CSA",
            "unconditional_stimulus": True,
            "trial_started_at": parse_datetime("2020-01-01T00:00Z"),
            "response_recorded_at": parse_datetime("2020-01-01T00:00Z"),
            "volume_level": "0.50",
            "headphones": True,
        }

        resp = self.client.post(url, json_data, content_type="application/json")

        self.assertEqual(201, resp.status_code)

        # Send the same data again (same trial, participant, and module)
        resp = self.client.post(url, json_data, content_type="application/json")

        self.assertEqual(400, resp.status_code)

        self.assertEqual(
            resp.json(),
            {
                "non_field_errors": [
                    "The fields trial, module, participant must make a unique set."
                ]
            },
        )
