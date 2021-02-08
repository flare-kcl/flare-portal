from django.db import models
from django.urls import reverse


class Voucher(models.Model):
    code = models.CharField(max_length=255)
    pool = models.ForeignKey(
        "reimbursement.VoucherPool",
        on_delete=models.CASCADE,
        related_name="vouchers",
    )
    participant = models.OneToOneField(
        "experiments.Participant",
        on_delete=models.PROTECT,
        related_name="voucher",
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = (
            "code",
            "pool",
        )

    def __str__(self) -> str:
        return self.code


class VoucherPool(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    success_message = models.TextField(
        blank=True,
        help_text="Message to display to participants when claiming a voucher. "
        "Useful for instructions on how to use the vouchers.",
    )
    empty_pool_message = models.TextField(
        blank=True,
        help_text="Message to display to participants when the voucher pool "
        "has run out of vouchers.",
    )

    def get_absolute_url(self) -> str:
        return reverse("reimbursement:voucher_pool_update", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        return self.name
