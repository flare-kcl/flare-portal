# Generated by Django 3.1.2 on 2020-12-09 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("experiments", "0017_basic_info_data_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="basicinfomodule",
            name="collect_headphone_label",
            field=models.BooleanField(default=False),
        ),
    ]
