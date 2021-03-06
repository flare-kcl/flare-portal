# Generated by Django 3.1.2 on 2020-12-07 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("experiments", "0016_basic_info_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="basicinfodata",
            name="headphone_label",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="basicinfodata",
            name="headphone_type",
            field=models.CharField(
                choices=[
                    ("in_ear", "In-ear"),
                    ("on_ear", "On-ear"),
                    ("over_ear", "Over-ear"),
                ],
                default="in_ear",
                max_length=8,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="basicinfodata",
            name="os_name",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="basicinfodata",
            name="os_version",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="basicinfodata",
            name="device_make",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="basicinfodata",
            name="device_model",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="basicinfodata",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=[
                    ("male", "Male"),
                    ("female", "Female"),
                    ("non_binary", "Non-binary"),
                    ("self_define", "Prefer to self-define"),
                    ("dont_know", "Don't know"),
                    ("no_answer", "Prefer not to answer"),
                ],
                default="male",
                max_length=24,
            ),
        ),
    ]
