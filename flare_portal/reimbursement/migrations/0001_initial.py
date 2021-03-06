# Generated by Django 3.1.4 on 2021-01-22 10:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("experiments", "0041_taskinstructionsmodule"),
    ]

    operations = [
        migrations.CreateModel(
            name="VoucherPool",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "empty_pool_message",
                    models.TextField(
                        blank=True,
                        help_text="Message to display to a participant when the voucher pool has run out of vouchers.",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Voucher",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("code", models.CharField(max_length=255)),
                (
                    "participant",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="voucher",
                        to="experiments.participant",
                    ),
                ),
                (
                    "pool",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vouchers",
                        to="reimbursement.voucherpool",
                    ),
                ),
            ],
        ),
    ]
