from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from enumfields import EnumField

from .enums import EventLogKind
from .fields import NullableIntegerSetSpecifierField


class Command(models.Model):

    executable_path = models.CharField(max_length=1000)

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
    accepted_parameters = JSONField()
    parameter_format_string = models.CharField(max_length=1000, default='')


class Job(models.Model):
    """
    Unit of work that can be ran by the system.
    """
    command = models.ForeignKey(Command, on_delete=models.PROTECT)
    parameters = JSONField()
    archived = models.BooleanField(default=False)


class ScheduledJob(models.Model):
    """
    Scheduling for a job to be ran at certain moment(s).

    The scheduling can define the job to be run just once or as a series
    of recurring events.
    """

    # metadata
    created_at = models.DateTimeField()
    #created_by = models.ForeignKey(settings.AUTH_USER_MODEL) # TODO: Do we need this?

    job = models.ForeignKey(Job, on_delete=models.PROTECT)

    enabled = models.BooleanField(default=True, verbose_name=_('enabled'))

    timezone = models.CharField(max_length=100)  # e.g. Europe/Helsinki
    years = NullableIntegerSetSpecifierField(
        value_range=(1970, 3000), verbose_name=_('years'))
    months = NullableIntegerSetSpecifierField(
        value_range=(1, 12), verbose_name=_('months'))
    days_of_month = NullableIntegerSetSpecifierField(
        value_range=(1, 31), verbose_name=_('days of month'))
    weekdays = NullableIntegerSetSpecifierField(
        value_range=(0, 6), verbose_name=_('weekdays'), help_text=_(
            'Limit execution to specified weekdays. '
            'The weekdays are mapped to integer values so that '
            '0=Sunday, 1=Monday, 2=Tuesday, ..., 6=Saturday.'))
    hours = NullableIntegerSetSpecifierField(
        value_range=(0, 23), verbose_name=_('hours'))
    minutes = NullableIntegerSetSpecifierField(
        value_range=(0, 59), verbose_name=_('minutes'))
    #seconds = NullableIntegerSetSpecifierField( # TODO: Probably too much precision for us?
    #    value_range=(0, 59), verbose_name=_('Seconds'))

    #next_run_at = models.DateTimeField( #TODO: Is this field needed?
    #    null=True, blank=True, db_index=True)


class JobEvent(models.Model):
    """
    Instance of a job currently running or ran in the past.
    """
    job = models.ForeignKey(Job, on_delete=models.PROTECT)
    started_at = models.DateTimeField()
    stopped_at = models.DateTimeField(null=True)
    exit_code = models.IntegerField(null=True)


class JobEventLogEntry(models.Model):
    """
    """
    event = models.ForeignKey(JobEvent, on_delete=models.PROTECT)
    time = models.DateTimeField()
    kind = EnumField(EventLogKind, max_length=30)
    text = models.TextField()
