from typing import Any, Dict, List

from django import forms
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView

from extra_views import InlineFormSetFactory, UpdateWithInlinesView

from .models import Voucher, VoucherPool


class VoucherPoolCreateView(CreateView):
    model = VoucherPool
    fields = ["name", "description", "empty_pool_message"]
    object = None

    def form_valid(self, form: forms.BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, f'Added new voucher pool "{self.object}"')
        return response


voucher_pool_create_view = VoucherPoolCreateView.as_view()


class VoucherInline(InlineFormSetFactory):
    model = Voucher
    fields = ["code"]
    factory_kwargs = {"extra": 0}


class VoucherPoolUpdateView(UpdateWithInlinesView):
    model = VoucherPool
    fields = ["name", "description", "empty_pool_message"]
    object = None
    inlines = [VoucherInline]

    def forms_valid(
        self, form: forms.BaseModelForm, inlines: List[forms.BaseModelFormSet]
    ) -> HttpResponse:
        response = super().forms_valid(form, inlines)
        messages.success(self.request, f'Updated voucher pool "{self.object}"')
        return response


voucher_pool_update_view = VoucherPoolUpdateView.as_view()


class VoucherPoolDeleteView(DeleteView):
    model = VoucherPool
    success_url = reverse_lazy("reimbursement:voucher_pool_list")

    def delete(
        self, request: HttpRequest, *args: Any, **kwargs: Dict[str, Any]
    ) -> HttpResponse:
        voucher_pool = self.get_object()
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, f'Deleted voucher pool "{voucher_pool}"')
        return response


voucher_pool_delete_view = VoucherPoolDeleteView.as_view()


class VoucherPoolListView(ListView):
    model = VoucherPool


voucher_pool_list_view = VoucherPoolListView.as_view()
