from typing import Optional

from django.contrib import admin
from django.db.models import Model
from django.http import HttpRequest

from .models import (
    Command, Job, JobRun, JobRunLogEntry, ScheduledJob, Timezone)


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
    list_display = ['started_at', 'stopped_at', 'job', 'exit_code']
    list_filter = ['exit_code']


@admin.register(JobRunLogEntry)
class JobRunLogEntryAdmin(ReadOnlyAdmin):
    date_hierarchy = 'time'
    list_display = ['time', 'run', 'number', 'kind', 'text']
    list_filter = ['kind']


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
