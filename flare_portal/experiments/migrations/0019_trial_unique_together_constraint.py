# Generated by Django 3.1.2 on 2020-12-09 13:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("experiments", "0018_basic_info_module_updates"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="fearconditioningdata",
            unique_together={("trial", "module", "participant")},
        ),
    ]