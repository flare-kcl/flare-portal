# Generated by Django 3.1.2 on 2020-12-07 08:19

from decimal import Decimal

from django.db import migrations, models


def forwards(apps, schema_editor):  # type: ignore
    FearConditioningData = apps.get_model("experiments.FearConditioningData")

    for data in FearConditioningData.objects.all():
        data.volume_level = Decimal(data.volume_level / 100)
        data.save()


class Migration(migrations.Migration):

    dependencies = [
        ("experiments", "0014_stimulus_verbose_name"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="fearconditioningdata",
            name="volume_level",
            field=models.DecimalField(decimal_places=2, max_digits=3),
        ),
    ]
