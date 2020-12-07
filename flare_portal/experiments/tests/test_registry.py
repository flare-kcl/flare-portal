from django.test import TestCase

from ..models import FearConditioningData, FearConditioningModule
from ..registry import DataViewsetRegistry, ModuleRegistry


class ModuleRegistryTest(TestCase):
    def test_register_module_create_view(self) -> None:
        registry = ModuleRegistry()

        registry.register(FearConditioningModule)

        self.assertEqual(
            registry.urls[0].pattern._route,
            "projects/<int:project_pk>/experiments/<int:experiment_pk>/modules/"
            "fear-conditioning/add/",
        )
        self.assertEqual(
            registry.urls[0].callback, registry.views["fear_conditioning_create"]
        )
        self.assertEqual(registry.urls[0].name, "fear_conditioning_create")
        self.assertEqual(registry.modules, [FearConditioningModule])


class DataViewsetRegistryTest(TestCase):
    def test_register_data_model(self) -> None:
        registry = DataViewsetRegistry()

        registry.register(FearConditioningData)

        self.assertEqual(registry.data_models, [FearConditioningData])

        # List view
        self.assertEqual(
            registry.urls[0].pattern._route,
            "projects/<int:project_pk>/experiments/<int:experiment_pk>/data/"
            "fear-conditioning/",
        )
        self.assertEqual(
            registry.urls[0].callback, registry.views["fear_conditioning_data_list"]
        )
        self.assertEqual(registry.urls[0].name, "fear_conditioning_data_list")

        # Detail view
        self.assertEqual(
            registry.urls[1].pattern._route,
            "projects/<int:project_pk>/experiments/<int:experiment_pk>/data/"
            "fear-conditioning/<int:data_pk>/",
        )
        self.assertEqual(
            registry.urls[1].callback, registry.views["fear_conditioning_data_detail"]
        )
        self.assertEqual(registry.urls[1].name, "fear_conditioning_data_detail")
