import csv
from typing import Any, Dict, List

from django import forms
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.generic import ListView, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, DeleteView, FormView

from extra_views import InlineFormSetFactory, UpdateWithInlinesView

from .forms import VoucherUploadForm
from .models import Voucher, VoucherPool


class VoucherPoolCreateView(CreateView):
    model = VoucherPool
    fields = ["name", "description", "success_message", "empty_pool_message"]
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

    def get_formset_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_formset_kwargs()
        kwargs["queryset"] = self.object.vouchers.select_related(
            "participant", "participant__experiment"
        )
        return kwargs


class VoucherPoolUpdateView(UpdateWithInlinesView):
    model = VoucherPool
    fields = ["name", "description", "success_message", "empty_pool_message"]
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


class VoucherUploadView(FormView):
    form_class = VoucherUploadForm
    template_name = "reimbursement/voucher_upload_form.html"
    voucher_pool: VoucherPool

    def get_success_url(self) -> str:
        return self.voucher_pool.get_absolute_url()

    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        self.voucher_pool = get_object_or_404(VoucherPool, pk=kwargs["pk"])
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["voucher_pool"] = self.voucher_pool
        return context

    def form_valid(  # type: ignore[override]
        self, form: VoucherUploadForm
    ) -> HttpResponse:
        # Parse Uploaded file
        row_count = form.cleaned_data["row_count"]
        vouchers = form.save(voucher_pool=self.voucher_pool)

        # If successful then add a message
        messages.success(
            self.request, f"{len(vouchers)}/{row_count} voucher codes uploaded"
        )

        return super().form_valid(form)


voucher_upload_view = VoucherUploadView.as_view()


class VoucherExportView(SingleObjectMixin, View):
    model = VoucherPool

    def get(self, *args: Any, **kwargs: Dict[str, Any]) -> HttpResponse:
        pool: VoucherPool = self.get_object()  # type: ignore

        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = f"attachment;filename={slugify(pool.name)}-vouchers.csv"

        writer = csv.DictWriter(
            response, fieldnames=["voucher_code", "experiment_code", "participant_id"]
        )
        writer.writeheader()

        vouchers = pool.vouchers.select_related(
            "participant", "participant__experiment"
        ).order_by("pk")
        for voucher in vouchers:
            writer.writerow(
                {
                    "voucher_code": voucher.code,
                    "experiment_code": voucher.participant.experiment.code
                    if voucher.participant
                    else "",
                    "participant_id": voucher.participant.participant_id
                    if voucher.participant
                    else "",
                }
            )

        return response


voucher_export_view = VoucherExportView.as_view()
