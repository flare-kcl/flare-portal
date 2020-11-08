from django.test import TestCase

from ..models import FearConditioningData, FearConditioningModule
from ..registry import ModuleRegistry


class ModuleRegistryTest(TestCase):
    def test_register_module(self) -> None:
        registry = ModuleRegistry()

        registry.register(FearConditioningModule, FearConditioningData)

        self.assertEqual(
            registry.urls[0].pattern._route,
            "projects/<int:project_pk>/experiments/<int:experiment_pk>/modules/"
            "fear-conditioning/add/",
        )
        self.assertEqual(
            registry.urls[0].callback, registry.views["fear_conditioning_create"]
        )
        self.assertEqual(registry.urls[0].name, "fear_conditioning_create")
