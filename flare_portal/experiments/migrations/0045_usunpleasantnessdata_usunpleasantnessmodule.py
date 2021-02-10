# Generated by Django 3.1.5 on 2021-02-05 17:41

from django.db import migrations, models
import django.db.models.deletion
import flare_portal.experiments.models.core
import flare_portal.experiments.models.modules


class Migration(migrations.Migration):

    dependencies = [
        (
            "experiments",
            "0044_postexperimentquestionsdata_postexperimentquestionsmodule",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="USUnpleasantnessModule",
            fields=[
                (
                    "basemodule_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="experiments.basemodule",
                    ),
                ),
                (
                    "label",
                    models.CharField(
                        blank=True,
                        help_text="Helps with identifying modules. The label isn't displayed to the participant.",
                        max_length=255,
                    ),
                ),
                (
                    "audible_keyword",
                    models.CharField(
                        help_text="How unpleasent did you find the ......?",
                        max_length=255,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(
                flare_portal.experiments.models.modules.Manageable,
                "experiments.basemodule",
            ),
        ),
        migrations.CreateModel(
            name="USUnpleasantnessData",
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
                ("rating", models.PositiveIntegerField()),
                (
                    "module",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="data",
                        to="experiments.usunpleasantnessmodule",
                    ),
                ),
                (
                    "participant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="experiments.participant",
                    ),
                ),
            ],
            options={
                "unique_together": {("participant", "module")},
            },
            bases=(flare_portal.experiments.models.core.Nameable, models.Model),
        ),
    ]