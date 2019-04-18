# Generated by Django 2.1.7 on 2019-04-18 06:36

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
                ('type', enumfields.fields.EnumField(enum=batchrun.enums.CommandType, max_length=30)),
                ('name', models.CharField(help_text='Name of the command to run e.g. name of a program in PATH or a full path to an executable, or name of a management command.', max_length=1000, verbose_name='name')),
                ('parameters', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='parameters')),
                ('parameter_format_string', models.CharField(blank=True, default='', max_length=1000, verbose_name='parameter format string')),
            ],
            options={
                'verbose_name': 'command',
                'verbose_name_plural': 'commands',
            },
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='modification time')),
                ('name', models.CharField(help_text='Descriptive name for the job', max_length=200, verbose_name='name')),
                ('comment', models.CharField(blank=True, max_length=500, verbose_name='comment')),
                ('arguments', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='arguments')),
                ('command', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='batchrun.Command', verbose_name='command')),
            ],
            options={
                'verbose_name': 'job',
                'verbose_name_plural': 'jobs',
            },
        ),
        migrations.CreateModel(
            name='JobRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField(db_index=True, verbose_name='start time')),
                ('stopped_at', models.DateTimeField(blank=True, null=True, verbose_name='stop time')),
                ('exit_code', models.IntegerField(blank=True, null=True, verbose_name='exit code')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='batchrun.Job', verbose_name='job')),
            ],
            options={
                'verbose_name': 'job run',
                'verbose_name_plural': 'job runs',
            },
        ),
        migrations.CreateModel(
            name='JobRunLogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(verbose_name='number')),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='time')),
                ('kind', enumfields.fields.EnumField(enum=batchrun.enums.EventLogKind, max_length=30, verbose_name='kind')),
                ('text', models.TextField(blank=True, verbose_name='text')),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='batchrun.JobRun', verbose_name='run')),
            ],
            options={
                'verbose_name': 'log entry of a job run',
                'verbose_name_plural': 'log entries of job runs',
                'ordering': ['run__started_at', 'run', 'number'],
            },
        ),
        migrations.CreateModel(
            name='ScheduledJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='modification time')),
                ('comment', models.CharField(blank=True, max_length=500, verbose_name='comment')),
                ('enabled', models.BooleanField(db_index=True, default=True, verbose_name='enabled')),
                ('years', batchrun.fields.IntegerSetSpecifierField(value_range=(1970, 2200), verbose_name='years')),
                ('months', batchrun.fields.IntegerSetSpecifierField(value_range=(1, 12), verbose_name='months')),
                ('days_of_month', batchrun.fields.IntegerSetSpecifierField(value_range=(1, 31), verbose_name='days of month')),
                ('weekdays', batchrun.fields.IntegerSetSpecifierField(help_text='Limit execution to specified weekdays. Use integer values to represent the weekdays with the following mapping: 0=Sunday, 1=Monday, 2=Tuesday, ..., 6=Saturday.', value_range=(0, 6), verbose_name='weekdays')),
                ('hours', batchrun.fields.IntegerSetSpecifierField(value_range=(0, 23), verbose_name='hours')),
                ('minutes', batchrun.fields.IntegerSetSpecifierField(value_range=(0, 59), verbose_name='minutes')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='batchrun.Job', verbose_name='job')),
            ],
            options={
                'verbose_name': 'scheduled job',
                'verbose_name_plural': 'scheduled jobs',
            },
        ),
        migrations.CreateModel(
            name='Timezone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the timezone, e.g. "Europe/Helsinki" or "UTC". See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for a list of possible values.', max_length=200, unique=True, verbose_name='name')),
            ],
            options={
                'verbose_name': 'timezone',
                'verbose_name_plural': 'timezones',
            },
        ),
        migrations.AddField(
            model_name='scheduledjob',
            name='timezone',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='batchrun.Timezone', verbose_name='timezone'),
        ),
    ]