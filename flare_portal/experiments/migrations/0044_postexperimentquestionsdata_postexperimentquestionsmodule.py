# Generated by Django 3.1.5 on 2021-02-03 18:17

from django.db import migrations, models
import django.db.models.deletion
import flare_portal.experiments.models.core
import flare_portal.experiments.models.modules


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0043_experiment_voucher_pool'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostExperimentQuestionsModule',
            fields=[
                ('basemodule_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='experiments.basemodule')),
                ('label', models.CharField(blank=True, help_text="Helps with identifying modules. The label isn't displayed to the participant.", max_length=255)),
                ('experiment_unpleasant_scale', models.BooleanField(verbose_name='How unpleasant did you find the experiment with the loud noises?')),
                ('did_follow_instructions', models.BooleanField(verbose_name='Did you follow the instructions fully during the session?')),
                ('were_headphones_removed', models.BooleanField(verbose_name='Did you remove your headphones at any point during the experiment?')),
                ('headphones_removal_reason', models.BooleanField(verbose_name='At what point did you remove your headphones?')),
                ('rating_attention', models.BooleanField(verbose_name='Were you paying attention throughout the task where you were rating images?')),
                ('task_environment', models.BooleanField(verbose_name='Where did you do the task?')),
                ('was_alone', models.BooleanField(verbose_name='Were there any other people in the room (or passing by) while you were doing the task?')),
                ('was_interrupted', models.BooleanField(verbose_name='Were you interrupted during the task?')),
            ],
            options={
                'abstract': False,
            },
            bases=(flare_portal.experiments.models.modules.Manageable, 'experiments.basemodule'),
        ),
        migrations.CreateModel(
            name='PostExperimentQuestionsData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('experiment_unpleasant_scale', models.PositiveIntegerField()),
                ('did_follow_insuctions', models.BooleanField(null=True)),
                ('were_headphones_removed', models.BooleanField(null=True)),
                ('headphones_removal_reason', models.CharField(max_length=255, null=True)),
                ('were_paying_attention', models.BooleanField(null=True)),
                ('task_enviroment', models.CharField(max_length=255, null=True)),
                ('was_alone', models.BooleanField(null=True)),
                ('was_interrupted', models.BooleanField(null=True)),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='experiments.participant')),
            ],
            options={
                'abstract': False,
            },
            bases=(flare_portal.experiments.models.core.Nameable, models.Model),
        ),
    ]
