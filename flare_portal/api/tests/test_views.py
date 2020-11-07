from django.test import TestCase
from django.urls import reverse

from flare_portal.experiments.factories import (
    ExperimentFactory,
    FearConditioningModuleFactory,
    ParticipantFactory,
)
from flare_portal.experiments.models import Experiment, FearConditioningModule


class ConfigurationAPIViewTest(TestCase):
    def test_post(self) -> None:
        experiment: Experiment = ExperimentFactory()
        ParticipantFactory(participant_id="Flare.ABCDEF", experiment=experiment)

        module1: FearConditioningModule = FearConditioningModuleFactory(
            experiment=experiment, sortorder=1
        )
        experiment.modules.add(module1)

        module2: FearConditioningModule = FearConditioningModuleFactory(
            experiment=experiment, sortorder=2
        )
        experiment.modules.add(module2)

        resp = self.client.post(
            reverse("api:configuration"), {"participant": "Flare.ABCDEF"}
        )

        self.assertEqual(200, resp.status_code)

        data = resp.json()

        self.assertEqual(
            data["experiment"], {"id": experiment.pk, "name": experiment.name},
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
                        "rating_delay": module1.rating_delay,
                    },
                },
                {
                    "id": module2.pk,
                    "type": "FEAR_CONDITIONING",
                    "config": {
                        "phase": module2.phase,
                        "trials_per_stimulus": module2.trials_per_stimulus,
                        "reinforcement_rate": module2.reinforcement_rate,
                        "rating_delay": module2.rating_delay,
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
