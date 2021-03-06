from django.test import TestCase
from django.urls import reverse

from flare_portal.users.factories import UserFactory

from ..models import SiteConfiguration


class SiteSettingsTest(TestCase):
    def test_settings(self) -> None:
        # Load global settings
        config = SiteConfiguration.get_solo()

        config.participant_terms_and_conditions = "T&Cs"

        config.save()

        config = SiteConfiguration.get_solo()

        self.assertEqual(config.participant_terms_and_conditions, "T&Cs")


class UpdateSiteSettings(TestCase):
    def test_permissions(self) -> None:
        # Only admins can edit site settings
        user = UserFactory()
        user.grant_role("RESEARCHER")
        user.save()

        self.client.force_login(user)

        url = reverse("site_config:update")

        resp = self.client.get(url)
        self.assertEqual(302, resp.status_code)

        user.grant_role("ADMIN")
        user.save()

        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code)

    def test_update(self) -> None:
        user = UserFactory()
        user.grant_role("ADMIN")
        user.save()

        self.client.force_login(user)

        url = reverse("site_config:update")

        resp = self.client.get(url)

        self.assertEqual(200, resp.status_code)

        form_data = {
            "terms_and_conditions": "New terms",
            "privacy_policy": "New policy",
        }

        resp = self.client.post(url, form_data, follow=True)

        self.assertRedirects(resp, url)

        self.assertEqual(
            str(list(resp.context["messages"])[0]),
            "Updated site configuration.",
        )
