from django.test import TestCase

from flare_portal.experiments.models import FearConditioningData

from ..registry import DataAPIRegistry


class DataRegistryTest(TestCase):
    def test_register(self) -> None:
        registry = DataAPIRegistry()

        registry.register(FearConditioningData)

        self.assertEqual(registry.urls[0].pattern._route, "fear-conditioning-data/")
        self.assertEqual(
            registry.urls[0].callback, registry.views["fear_conditioning_data"]
        )
        self.assertEqual(registry.urls[0].name, "fear_conditioning_data")
        self.assertEqual(registry.data_models, [FearConditioningData])
