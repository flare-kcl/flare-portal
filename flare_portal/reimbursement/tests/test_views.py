import csv
import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from flare_portal.experiments.factories import ExperimentFactory, ParticipantFactory
from flare_portal.users.factories import UserFactory

from ..factories import VoucherFactory, VoucherPoolFactory
from ..models import VoucherPool


class VoucherPoolViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("ADMIN")
        self.user.save()
        self.client.force_login(self.user)

    def test_create(self) -> None:
        url = reverse("reimbursement:voucher_pool_create")
        resp = self.client.get(url)

        self.assertEqual(200, resp.status_code)

        form_data = {"name": "Voucher pool 1"}

        resp = self.client.post(url, form_data, follow=True)

        pool = VoucherPool.objects.get()

        self.assertRedirects(resp, pool.get_absolute_url())

        self.assertEqual(pool.name, "Voucher pool 1")
        self.assertEqual(
            str(list(resp.context["messages"])[0]), f'Added new voucher pool "{pool}"'
        )

    def test_update(self) -> None:
        pool = VoucherPoolFactory()

        url = reverse("reimbursement:voucher_pool_update", kwargs={"pk": pool.pk})
        resp = self.client.get(url)

        self.assertEqual(200, resp.status_code)

        form_data = {
            "name": "My voucher pool",
            "vouchers-TOTAL_FORMS": "3",
            "vouchers-INITIAL_FORMS": "0",
            "vouchers-MIN_NUM_FORMS": "0",
            "vouchers-MAX_NUM_FORMS": "1000",
            "vouchers-0-id": "",
            "vouchers-0-code": "First voucher",
            "vouchers-0-DELETE": "",
            "vouchers-1-id": "",
            "vouchers-1-code": "Second voucher",
            "vouchers-1-DELETE": "",
        }

        resp = self.client.post(url, form_data, follow=True)

        pool.refresh_from_db()

        self.assertRedirects(resp, pool.get_absolute_url())

        self.assertEqual(pool.name, "My voucher pool")

        vouchers = pool.vouchers.all()

        self.assertEqual(2, len(vouchers))

        self.assertEqual("First voucher", vouchers[0].code)
        self.assertEqual("Second voucher", vouchers[1].code)

        self.assertEqual(
            str(list(resp.context["messages"])[0]), f'Updated voucher pool "{pool}"'
        )

    def test_delete(self) -> None:
        pool = VoucherPoolFactory()

        url = reverse("reimbursement:voucher_pool_delete", kwargs={"pk": pool.pk})
        resp = self.client.get(url)

        self.assertEqual(200, resp.status_code)

        resp = self.client.post(url, follow=True)

        self.assertRedirects(resp, reverse("reimbursement:voucher_pool_list"))

        with self.assertRaises(VoucherPool.DoesNotExist):
            VoucherPool.objects.get(pk=pool.pk)

        self.assertEqual(
            str(list(resp.context["messages"])[0]), f'Deleted voucher pool "{pool}"'
        )

    def test_list(self) -> None:
        VoucherPoolFactory.create_batch(3)

        url = reverse("reimbursement:voucher_pool_list")
        resp = self.client.get(url)

        self.assertEqual(200, resp.status_code)

        self.assertEqual(3, len(resp.context["object_list"]))

    def test_permissions(self) -> None:
        pool = VoucherPoolFactory()

        # Only admins can access vouchers
        researcher = UserFactory()
        researcher.grant_role("RESEARCHER")
        researcher.save()

        admin = UserFactory()
        admin.grant_role("ADMIN")
        admin.save()

        urls = [
            reverse("reimbursement:voucher_pool_list"),
            reverse("reimbursement:voucher_pool_create"),
            reverse("reimbursement:voucher_pool_update", kwargs={"pk": pool.pk}),
            reverse("reimbursement:voucher_pool_delete", kwargs={"pk": pool.pk}),
            reverse("reimbursement:voucher_upload", kwargs={"pk": pool.pk}),
        ]

        self.client.force_login(researcher)

        for url in urls:
            with self.subTest(url):
                resp = self.client.get(url)
                self.assertEqual(302, resp.status_code)

        self.client.force_login(admin)

        for url in urls:
            with self.subTest(url):
                resp = self.client.get(url)
                self.assertEqual(200, resp.status_code)


class VoucherUploadViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("ADMIN")
        self.user.save()
        self.client.force_login(self.user)

    def test_upload(self) -> None:
        pool = VoucherPoolFactory()

        url = reverse("reimbursement:voucher_upload", kwargs={"pk": pool.pk})

        # Check form view loads
        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code)

        # Get the CSV import template
        csv_file = open("flare_portal/static_src/misc/voucher-pool-template.csv", "rb")
        template = SimpleUploadedFile(
            "voucher-pool-template.csv", csv_file.read(), content_type="text/csv"
        )
        form_data = {"import_file": template}

        # Submit upload form
        resp = self.client.post(url, form_data, follow=True)

        # Check it redirects successfully
        self.assertRedirects(
            resp,
            reverse("reimbursement:voucher_pool_update", kwargs={"pk": pool.pk}),
        )

        # Check each code in the file has been created
        vouchers = pool.vouchers.order_by("pk")

        self.assertEqual("voucher code 1", vouchers[0].code)
        self.assertEqual("voucher code 2", vouchers[1].code)
        self.assertEqual("voucher code 3", vouchers[2].code)

        self.assertEqual(
            str(list(resp.context["messages"])[0]),
            "3/3 voucher codes uploaded",
        )

    def test_upload_without_duplicates(self) -> None:
        pool = VoucherPoolFactory()
        VoucherFactory(pool=pool, code="voucher code 1")
        VoucherFactory(pool=pool, code="voucher code 2")

        url = reverse("reimbursement:voucher_upload", kwargs={"pk": pool.pk})

        # Check form view loads
        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code)

        # Get the CSV import template
        csv_file = open("flare_portal/static_src/misc/voucher-pool-template.csv", "rb")
        template = SimpleUploadedFile(
            "voucher-pool-template.csv", csv_file.read(), content_type="text/csv"
        )
        form_data = {"import_file": template}

        # Submit upload form
        resp = self.client.post(url, form_data, follow=True)

        # Check it redirects successfully
        self.assertRedirects(
            resp,
            reverse("reimbursement:voucher_pool_update", kwargs={"pk": pool.pk}),
        )

        # Check each code in the file has been created
        vouchers = pool.vouchers.order_by("pk")

        self.assertEqual(3, len(vouchers))
        self.assertEqual("voucher code 1", vouchers[0].code)
        self.assertEqual("voucher code 2", vouchers[1].code)
        self.assertEqual("voucher code 3", vouchers[2].code)

        self.assertEqual(
            str(list(resp.context["messages"])[0]),
            "1/3 voucher codes uploaded",
        )


class VoucherExportViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user.grant_role("ADMIN")
        self.user.save()
        self.client.force_login(self.user)

    def test_export(self) -> None:
        pool = VoucherPoolFactory()
        vouchers = VoucherFactory.create_batch(10, pool=pool)
        experiment = ExperimentFactory(voucher_pool=pool)
        participant = ParticipantFactory(experiment=experiment)
        vouchers[0].participant = participant
        vouchers[0].save()

        url = reverse("reimbursement:voucher_export", kwargs={"pk": pool.pk})

        resp = self.client.get(url)

        reader = csv.DictReader(io.StringIO(resp.content.decode("utf-8")))

        rows = [row for row in reader]

        self.assertEqual(10, len(rows))

        for index, voucher in enumerate(vouchers):
            self.assertEqual(voucher.code, rows[index]["voucher_code"])

        self.assertEqual(
            rows[0],
            {
                "voucher_code": vouchers[0].code,
                "experiment_code": experiment.code,
                "participant_id": participant.participant_id,
            },
        )
