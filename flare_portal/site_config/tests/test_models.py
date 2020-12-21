from django.test import TestCase

from ..models import SiteConfiguration


class SiteSettingsTest(TestCase):
    def test_settings(self):
        # Load global settings
        config = SiteConfiguration.get_solo()

        self.assertEqual(config.terms_and_conditions, "")

        config.terms_and_conditions = "T&Cs"

        config.save()

        config = SiteConfiguration.get_solo()

        self.assertEqual(config.terms_and_conditions, "T&Cs")
