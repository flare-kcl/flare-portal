# Generated by Django 3.1.5 on 2021-02-17 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0050_module_tracking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fearconditioningdata',
            name='conditional_stimulus',
            field=models.CharField(max_length=24, verbose_name='stimulus'),
        ),
        migrations.AlterField(
            model_name='fearconditioningdata',
            name='headphones',
            field=models.BooleanField(verbose_name='headphones connected'),
        ),
        migrations.AlterField(
            model_name='fearconditioningdata',
            name='volume_level',
            field=models.DecimalField(decimal_places=2, max_digits=3, verbose_name='device volume level'),
        ),
        migrations.AlterField(
            model_name='taskinstructionsmodule',
            name='intro_body',
            field=models.TextField(blank=True, default='Before you begin the experiment, we need to practice using the rating interface.', help_text='Text on the task instructions intro screen'),
        ),
        migrations.AlterField(
            model_name='taskinstructionsmodule',
            name='outro_body',
            field=models.TextField(blank=True, default='The experiment will now begin.\n\n You may occasionaly hear a scream.\n\n Remember to rate how much you expect to hear a scream by pressing a number every time the scale appears.', help_text='Text on the task instructions outro screen'),
        ),
    ]