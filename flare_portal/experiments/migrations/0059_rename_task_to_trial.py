# Generated by Django 3.1.6 on 2021-03-12 08:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0058_experiment_minimum_volume'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fearconditioningdata',
            old_name='did_leave_task',
            new_name='did_leave_trial',
        ),
    ]
