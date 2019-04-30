from typing import Optional

from django.contrib import admin
from django.db.models import Model
from django.http import HttpRequest
from django.utils.translation import ugettext_lazy as _

from .models import (
    Command, Job, JobRun, JobRunLogEntry, JobRunQueueItem, ScheduledJob,
    Timezone)


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(
            self,
            request: HttpRequest,
            obj: Optional[Model] = None,
    ) -> bool:
        return False

    def has_change_permission(
            self,
            request: HttpRequest,
            obj: Optional[Model] = None,
    ) -> bool:
        return False

    def has_delete_permission(
            self,
            request: HttpRequest,
            obj: Optional[Model] = None,
    ) -> bool:
        return False


@admin.register(Command)
class CommandAdmin(admin.ModelAdmin):
    list_display = ['type', 'name']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['name', 'comment', 'command']


@admin.register(JobRun)
class JobRunAdmin(ReadOnlyAdmin):
    date_hierarchy = 'started_at'
    list_display = [
        'precise_started_at', 'precise_stopped_at',
        'job', 'exit_code']
    list_filter = ['exit_code']

    def precise_started_at(self, obj: Model) -> str:
        return obj.started_at.strftime('%Y-%m-%d %H:%M:%S.%f')  # type: ignore
    precise_started_at.short_description = _('start time')  # type: ignore
    precise_started_at.admin_order_field = 'started_at'  # type: ignore

    def precise_stopped_at(self, obj: Model) -> str:
        return obj.stopped_at.strftime('%Y-%m-%d %H:%M:%S.%f')  # type: ignore
    precise_stopped_at.short_description = _('start time')  # type: ignore
    precise_stopped_at.admin_order_field = 'stopped_at'  # type: ignore


@admin.register(JobRunLogEntry)
class JobRunLogEntryAdmin(ReadOnlyAdmin):
    date_hierarchy = 'time'
    list_display = [
        'precise_time', 'run', 'kind', 'line_number', 'number', 'text']
    list_filter = ['kind']

    def precise_time(self, obj: Model) -> str:
        return obj.time.strftime('%Y-%m-%d %H:%M:%S.%f')  # type: ignore
    precise_time.short_description = _('time')  # type: ignore
    precise_time.admin_order_field = 'time'  # type: ignore


@admin.register(JobRunQueueItem)
class JobRunQueueItemAdmin(ReadOnlyAdmin):
    date_hierarchy = 'run_at'
    list_display = ['run_at', 'scheduled_job', 'assigned_at', 'assignee_pid']


@admin.register(ScheduledJob)
class ScheduledJobAdmin(admin.ModelAdmin):
    list_display = [
        'job', 'enabled', 'comment',
        'years', 'months', 'days_of_month', 'weekdays', 'hours', 'minutes',
        'timezone',
    ]
    list_filter = ['enabled']


@admin.register(Timezone)
class TimezoneAdmin(admin.ModelAdmin):
    pass
