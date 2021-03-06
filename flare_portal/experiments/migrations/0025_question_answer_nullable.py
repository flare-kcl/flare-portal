# Generated by Django 3.1.4 on 2020-12-17 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("experiments", "0024_criterion_required_answer"),
    ]

    operations = [
        migrations.AlterField(
            model_name="criteriondata",
            name="answer",
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name="criterionquestion",
            name="required_answer",
            field=models.BooleanField(
                blank=True,
                choices=[(None, "Yes or No"), (True, "Yes"), (False, "No")],
                default=None,
                null=True,
            ),
        ),
    ]
