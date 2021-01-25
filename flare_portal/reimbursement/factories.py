import factory

from .models import Voucher, VoucherPool


class VoucherPoolFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VoucherPool

    name = factory.Sequence(lambda n: f"voucher_pool_{n}")


class VoucherFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Voucher

    code = factory.Sequence(lambda n: f"voucher_{n}")
    pool = factory.SubFactory(VoucherPoolFactory)
