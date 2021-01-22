import factory

from .models import VoucherPool


class VoucherPoolFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VoucherPool

    name = factory.Sequence(lambda n: f"voucher_pool_{n}")
