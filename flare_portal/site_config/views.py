from typing import Any

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic.edit import FormView

from .forms import SiteConfigurationUpdateForm
from .models import SiteConfiguration


class SiteConfigurationUpdateFormView(FormView):
    form_class = SiteConfigurationUpdateForm  # type: ignore
    template_name = "site_config/siteconfiguration_form.html"

    def get_form_kwargs(self) -> dict:
        return {**super().get_form_kwargs(), "instance": SiteConfiguration.get_solo()}

    def get_success_url(self) -> str:
        return reverse("site_config:update")

    def form_valid(self, form: Any) -> HttpResponse:
        form.save()
        messages.success(self.request, "Updated site configuration.")
        return super().form_valid(form)


site_configuration_update_view = SiteConfigurationUpdateFormView.as_view()


def participant_privacy_policy_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(
        request,
        "site_config/markdown-article.html",
        {
            "title": "FLARe App - Participant Privacy Policy",
            "content": SiteConfiguration.get_solo().participant_privacy_policy,
        },
    )


def researcher_privacy_policy_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(
        request,
        "site_config/markdown-article.html",
        {
            "title": "FLARe App - Researcher Privacy Policy",
            "content": SiteConfiguration.get_solo().researcher_privacy_policy,
        },
    )


def participant_terms_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(
        request,
        "site_config/markdown-article.html",
        {
            "title": "FLARe App - Participant Terms & Conditions",
            "content": SiteConfiguration.get_solo().participant_terms_and_conditions,
        },
    )


def researcher_terms_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(
        request,
        "site_config/markdown-article.html",
        {
            "title": "FLARe App - Researcher Terms & Conditions",
            "content": SiteConfiguration.get_solo().researcher_terms_and_conditions,
        },
    )
