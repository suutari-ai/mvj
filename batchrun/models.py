import os
import shlex
import sys
from datetime import timedelta
from typing import Any, Dict, List

import pytz
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from enumfields import EnumField

from ._times import utc_now
from .enums import CommandType, LogEntryKind
from .fields import IntegerSetSpecifierField
from .model_mixins import CleansOnSave, TimeStampedSafeDeleteModel
from .scheduling import RecurrenceRule, get_next_events


class Command(models.Model):
    type = EnumField(CommandType, max_length=30)

    name = models.CharField(
        max_length=1000, verbose_name=_('name'), help_text=_(
            'Name of the command to run e.g. '
            'name of a program in PATH or a full path to an executable, or '
            'name of a management command.'))

    # type definition for each parameter, e.g.:
    #   {
    #     "rent_id": {
    #       "type": "int",
    #       "required": false,
    #       "description": {
    #         "fi": "Vuokrauksen tunnus",
    #         "sv": ...
    #       }
    #     },
    #     "time_range_start": {"type": "datetime", "required": true},
    #     "time_range_end": ...
    #   }
    parameters = JSONField(
        default=dict, blank=True, verbose_name=_('parameters'))
    parameter_format_string = models.CharField(
        max_length=1000, default='', blank=True,
        verbose_name=_('parameter format string'))

    class Meta:
        verbose_name = _('command')
        verbose_name_plural = _('commands')

    def __str__(self) -> str:
        return '{type}: {name}{space}{params}'.format(
            type=self.type,
            name=self.name,
            space=' ' if self.parameter_format_string else '',
            params=self.parameter_format_string)

    def get_command_line(self, arguments: Dict[str, Any]) -> List[str]:
        if self.type == CommandType.EXECUTABLE:
            base_command = [self.name]
        elif self.type == CommandType.DJANGO_MANAGE:
            base_command = [sys.executable, get_django_manage_py(), self.name]
        else:
            raise ValueError('Unknown command type: {}'.format(self.type))
        formatted_args = [
            param_template.format(arguments)
            for param_template in shlex.split(self.parameter_format_string)
        ]
        return base_command + formatted_args


def get_django_manage_py(max_depth: int = 3) -> str:
    manage_py_path = getattr(settings, 'MANAGE_PY_PATH', None)
    if manage_py_path:
        if not isinstance(manage_py_path, str):
            raise ImproperlyConfigured('MANAGE_PY_PATH should be a string')
        return manage_py_path

    # Try to auto detect by searching down from dir containing settings
    settings_mod = sys.modules[settings.SETTINGS_MODULE]  # type: ignore
    directory = os.path.dirname(settings_mod.__file__)
    tries_left = max_depth
    while directory != '/' and tries_left:
        candidate = os.path.join(directory, 'manage.py')
        if os.path.exists(candidate):
            return candidate
        tries_left -= 1
        directory = os.path.dirname(directory)
    raise EnvironmentError('Cannot find manage.py')


class Job(TimeStampedSafeDeleteModel):
    """
    Unit of work that can be ran by the system.

    Job is basically a Command with predefined arguments to be passed as
    the parameters for the command.  E.g. command can be Django's
    "migrate" management command and a job could then be "Migrate app1"
    which passes in the "app1" argument as "app_label" parameter.
    """
    name = models.CharField(
        max_length=200, verbose_name=_('name'), help_text=_(
            'Descriptive name for the job'))
    comment = models.CharField(
        max_length=500, blank=True, verbose_name=_('comment'))

    command = models.ForeignKey(
        Command, on_delete=models.PROTECT, verbose_name=_('command'))
    arguments = JSONField(
        default=dict, blank=True, verbose_name=_('arguments'))

    class Meta:
        verbose_name = _('job')
        verbose_name_plural = _('jobs')

    def __str__(self) -> str:
        return self.name

    def get_command_line(self) -> List[str]:
        return self.command.get_command_line(self.arguments)


class Timezone(CleansOnSave, models.Model):
    name = models.CharField(
        max_length=200, unique=True, verbose_name=_('name'), help_text=_(
            'Name of the timezone, e.g. "Europe/Helsinki" or "UTC". See '
            'https://en.wikipedia.org/wiki/List_of_tz_database_time_zones '
            'for a list of possible values.'))

    class Meta:
        verbose_name = _('timezone')
        verbose_name_plural = _('timezones')

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        try:
            pytz.timezone(self.name or '')
        except KeyError:
            raise ValidationError({'name': _('Invalid timezone name')})
        super().clean()


class ScheduledJob(TimeStampedSafeDeleteModel):
    """
    Scheduling for a job to be ran at certain moment(s).

    The scheduling can define the job to be run just once or as a series
    of recurring events.
    """
    job = models.ForeignKey(
        Job, on_delete=models.PROTECT, verbose_name=_('job'))

    comment = models.CharField(
        max_length=500, blank=True, verbose_name=_('comment'))

    enabled = models.BooleanField(
        default=True, db_index=True, verbose_name=_('enabled'))

    timezone = models.ForeignKey(
        Timezone, on_delete=models.PROTECT, verbose_name=_('timezone'))
    years = IntegerSetSpecifierField(
        value_range=(1970, 2200), verbose_name=_('years'))
    months = IntegerSetSpecifierField(
        value_range=(1, 12), verbose_name=_('months'))
    days_of_month = IntegerSetSpecifierField(
        value_range=(1, 31), verbose_name=_('days of month'))
    weekdays = IntegerSetSpecifierField(
        value_range=(0, 6), verbose_name=_('weekdays'), help_text=_(
            'Limit execution to specified weekdays. Use integer values '
            'to represent the weekdays with the following mapping: '
            '0=Sunday, 1=Monday, 2=Tuesday, ..., 6=Saturday.'))
    hours = IntegerSetSpecifierField(
        value_range=(0, 23), verbose_name=_('hours'))
    minutes = IntegerSetSpecifierField(
        value_range=(0, 59), verbose_name=_('minutes'))

    class Meta:
        verbose_name = _('scheduled job')
        verbose_name_plural = _('scheduled jobs')

    def __str__(self) -> str:
        time_fields = [
            'years', 'months', 'days_of_month', 'weekdays',
            'hours', 'minutes']
        schedule_items = []
        for field in time_fields:
            value = getattr(self, field)
            key = (field[0] if field not in ['hours', 'minutes'] else
                   field[0].upper())
            schedule_items.append(f'{key}={value}')
        return ugettext('Scheduled job "{job}" @ {schedule}').format(
            job=self.job, schedule=' '.join(schedule_items))

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)
        self.update_run_queue()

    def update_run_queue(self) -> None:
        max_items_to_create = 60

        recurrence_rule = RecurrenceRule.create(
            timezone=self.timezone.name,
            years=self.years,
            months=self.months,
            days_of_month=self.days_of_month,
            weekdays=self.weekdays,
            hours=self.hours,
            minutes=self.minutes)

        items: models.Manager = self.run_queue_items  # type: ignore

        # Delete old items
        items.all().delete()

        if self.enabled:
            # Create new items till the time limit
            events = get_next_events(recurrence_rule, utc_now())
            for (number, time) in enumerate(events):
                if number >= max_items_to_create:
                    break
                items.create(run_at=time, scheduled_job=self)


class JobRun(models.Model):
    """
    Instance of a job currently running or ran in the past.
    """
    job = models.ForeignKey(
        Job, on_delete=models.PROTECT, verbose_name=_('job'))
    pid = models.IntegerField(
        null=True, blank=True, verbose_name=_('PID'), help_text=_(
            'Records the process id of the process, '
            'which is/was executing this job'))
    started_at = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_('start time'))
    stopped_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_('stop time'))
    exit_code = models.IntegerField(
        null=True, blank=True, verbose_name=_('exit code'))

    class Meta:
        verbose_name = _('job run')
        verbose_name_plural = _('job runs')

    def __str__(self) -> str:
        return f'{self.job} [{self.pid}] ({self.started_at:%Y-%m-%dT%H:%M})'


class JobRunLogEntry(models.Model):
    """
    Entry in a log for a run of a job.

    A log is stored for each run of a job.  The log contains a several
    entries which are ordered by the "number" field in this model.  Each
    entry generally stores a line of output from either stdout or stderr
    stream.  The source stream is stored into the "kind" field.
    Additionally a creation timestamp is recorded to the "time" field.
    """
    run = models.ForeignKey(
        JobRun, on_delete=models.PROTECT, related_name='log_entries',
        verbose_name=_('run'))
    kind = EnumField(LogEntryKind, max_length=30, verbose_name=_('kind'))
    line_number = models.IntegerField(verbose_name=_('line number'))
    number = models.IntegerField(verbose_name=_('number'))  # within line
    time = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_('time'))
    text = models.TextField(null=False, blank=True, verbose_name=_('text'))

    class Meta:
        ordering = ['run__started_at', 'run', 'time']
        verbose_name = _('log entry of a job run')
        verbose_name_plural = _('log entries of job runs')

    def __str__(self) -> str:
        return ugettext('{run_name}: {kind} entry {number}').format(
            run_name=self.run, kind=self.kind, number=self.number)


class JobRunQueueItem(models.Model):
    run_at = models.DateTimeField(
        db_index=True, verbose_name=_('scheduled run time'))
    scheduled_job = models.ForeignKey(
        ScheduledJob, on_delete=models.CASCADE,
        related_name='run_queue_items', verbose_name=_('scheduled job'))

    assigned_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_('assignment time'))
    assignee_pid = models.IntegerField(
        null=True, blank=True, verbose_name=_('assignee process id (PID)'))

    class Meta:
        ordering = ['run_at']

    def __str__(self) -> str:
        return f'{self.run_at}: {self.scheduled_job}'
