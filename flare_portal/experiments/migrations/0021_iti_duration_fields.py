# Generated by Django 3.1.2 on 2020-12-15 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0020_cs_verbose_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='iti_max_delay',
            field=models.PositiveIntegerField(default=3),
        ),
        migrations.AddField(
            model_name='experiment',
            name='iti_min_delay',
            field=models.PositiveIntegerField(default=1),
        ),
    ]