from django import forms
from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView

from .models import SiteConfiguration


class SiteConfigurationUpdateView(UpdateView):
    fields = "__all__"
    model = SiteConfiguration
    success_url = reverse_lazy("site_config:update")

    def get_object(
        self, queryset: QuerySet[SiteConfiguration] = None
    ) -> SiteConfiguration:
        return SiteConfiguration.get_solo()

    def form_valid(self, form: forms.BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, "Updated site configuration.")
        return response


site_configuration_update_view = SiteConfigurationUpdateView.as_view()