# Generated by Django 3.1.5 on 2021-01-21 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0041_taskinstructionsmodule'),
    ]

    operations = [
        migrations.AddField(
            model_name='affectiveratingmodule',
            name='label',
            field=models.CharField(blank=True, help_text="Helps with identifying modules. The label isn't displayed to the participant.", max_length=255),
        ),
        migrations.AddField(
            model_name='basicinfomodule',
            name='label',
            field=models.CharField(blank=True, help_text="Helps with identifying modules. The label isn't displayed to the participant.", max_length=255),
        ),
        migrations.AddField(
            model_name='criterionmodule',
            name='label',
            field=models.CharField(blank=True, help_text="Helps with identifying modules. The label isn't displayed to the participant.", max_length=255),
        ),
        migrations.AddField(
            model_name='fearconditioningmodule',
            name='label',
            field=models.CharField(blank=True, help_text="Helps with identifying modules. The label isn't displayed to the participant.", max_length=255),
        ),
        migrations.AddField(
            model_name='instructionsmodule',
            name='label',
            field=models.CharField(blank=True, help_text="Helps with identifying modules. The label isn't displayed to the participant.", max_length=255),
        ),
        migrations.AddField(
            model_name='taskinstructionsmodule',
            name='label',
            field=models.CharField(blank=True, help_text="Helps with identifying modules. The label isn't displayed to the participant.", max_length=255),
        ),
        migrations.AddField(
            model_name='textmodule',
            name='label',
            field=models.CharField(blank=True, help_text="Helps with identifying modules. The label isn't displayed to the participant.", max_length=255),
        ),
        migrations.AddField(
            model_name='webmodule',
            name='label',
            field=models.CharField(blank=True, help_text="Helps with identifying modules. The label isn't displayed to the participant.", max_length=255),
        ),
    ]
