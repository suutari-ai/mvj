# Generated by Django 2.1.7 on 2019-04-16 05:55

import batchrun.enums
import batchrun.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import enumfields.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Command',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('executable_path', models.CharField(max_length=1000)),
                ('accepted_parameters', django.contrib.postgres.fields.jsonb.JSONField()),
                ('parameter_format_string', models.CharField(default='', max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameters', django.contrib.postgres.fields.jsonb.JSONField()),
                ('archived', models.BooleanField(default=False)),
                ('command', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='batchrun.Command')),
            ],
        ),
        migrations.CreateModel(
            name='JobRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField()),
                ('stopped_at', models.DateTimeField(null=True)),
                ('exit_code', models.IntegerField(null=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='batchrun.Job')),
            ],
        ),
        migrations.CreateModel(
            name='JobRunLogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('kind', enumfields.fields.EnumField(enum=batchrun.enums.EventLogKind, max_length=30)),
                ('text', models.TextField()),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='batchrun.JobRun')),
            ],
        ),
        migrations.CreateModel(
            name='ScheduledJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('enabled', models.BooleanField(default=True, verbose_name='enabled')),
                ('timezone', models.CharField(max_length=100)),
                ('years', batchrun.fields.IntegerSetSpecifierField(value_range=(1970, 2200), verbose_name='years')),
                ('months', batchrun.fields.IntegerSetSpecifierField(value_range=(1, 12), verbose_name='months')),
                ('days_of_month', batchrun.fields.IntegerSetSpecifierField(value_range=(1, 31), verbose_name='days of month')),
                ('weekdays', batchrun.fields.IntegerSetSpecifierField(help_text='Limit execution to specified weekdays. The weekdays are mapped to integer values so that 0=Sunday, 1=Monday, 2=Tuesday, ..., 6=Saturday.', value_range=(0, 6), verbose_name='weekdays')),
                ('hours', batchrun.fields.IntegerSetSpecifierField(value_range=(0, 23), verbose_name='hours')),
                ('minutes', batchrun.fields.IntegerSetSpecifierField(value_range=(0, 59), verbose_name='minutes')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='batchrun.Job')),
            ],
        ),
    ]
