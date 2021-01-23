import django.core.paginator
from django.contrib import admin
from rangefilter.filter import DateRangeFilter  # type: ignore

from .admin_utils import PreciseTimeFormatter, ReadOnlyAdmin
from .models import (
    Command,
    Job,
    JobRun,
    JobRunLogEntry,
    JobRunQueueItem,
    ScheduledJob,
    Timezone,
)


@admin.register(Command)
class CommandAdmin(admin.ModelAdmin):
    list_display = ["type", "name"]
    exclude = ["parameters"]


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ["name", "comment", "command"]


class JobRunLogEntryInline(admin.TabularInline):
    model = JobRunLogEntry
    show_change_link = True


@admin.register(JobRun)
class JobRunAdmin(ReadOnlyAdmin):
    date_hierarchy = "started_at"
    inlines = [JobRunLogEntryInline]
    list_display = ["started_at_p", "stopped_at_p", "job", "exit_code"]
    list_filter = ("started_at", ("started_at", DateRangeFilter), "job", "exit_code")
    # auto_now_add_fields don't show even in readonlyadmin.
    # Therefore we'll add all the fields by hand in a suitable order
    readonly_fields = ("job", "pid", "started_at_p", "stopped_at_p", "exit_code")
    search_fields = ["log_entries__text"]
    exclude = ["stopped_at"]

    started_at_p = PreciseTimeFormatter(JobRun, "started_at")
    stopped_at_p = PreciseTimeFormatter(JobRun, "stopped_at")

#from .paginator import Paginator

from django.contrib.admin.views.main import ChangeList

class CustomChangeList(ChangeList):
    def get_results(self, request):
        paginator = self.model_admin.get_paginator(request, self.queryset, self.list_per_page)
        # Get the number of objects, with admin filters applied.
        result_count = paginator.count

        # Get the total number of objects, with no admin filters applied.
        if self.model_admin.show_full_result_count:
            full_result_count = self.root_queryset.count()
        else:
            full_result_count = None
        can_show_all = result_count <= self.list_max_show_all
        multi_page = result_count > self.list_per_page

        # Get the list of objects to display on this page.
        if (self.show_all and can_show_all) or not multi_page:
            result_list = self.queryset._clone()
        else:
            try:
                result_list = paginator.page(self.page_num + 1).object_list
            except InvalidPage:
                raise IncorrectLookupParameters

        self.result_count = result_count
        self.show_full_result_count = self.model_admin.show_full_result_count
        # Admin actions are shown if there is at least one entry
        # or if entries are not counted because show_full_result_count is disabled
        self.show_admin_actions = not self.show_full_result_count or bool(full_result_count)
        self.full_result_count = full_result_count
        self.result_list = result_list
        self.can_show_all = can_show_all
        self.multi_page = multi_page
        self.paginator = paginator
        


class Paginator(django.core.paginator.Paginator):
    @property
    def count(self):
        return 999_999_999_999

from django.utils import timezone
from datetime import timedelta


@admin.register(JobRunLogEntry)
class JobRunLogEntryAdmin(ReadOnlyAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.resolver_match.kwargs.get("object_id"):
            print("XXXXXXXXXXXXXXXXXX get_queryset: with object_id")
            return qs
        #print(request)
        #import ipdb; ipdb.set_trace()
        block_idx = 1  # 0 = -30d..now, 1 = -60d..-30d, 2 = -90d..-60d, ...
        block_len = timedelta(days=200)
        start = (timezone.now() - block_len * (block_idx + 1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = (timezone.now() - block_len * block_idx).replace(hour=0, minute=0, second=0, microsecond=0)
        print("XXXXXXXXXXXXXXXXXX get_queryset: no object LIMITING!!!!!!!!!!!!!!")
        return qs.filter(time__gt=start, time__lte=end)
    
    search_fields = ["run__job__name", "text"]
    #date_hierarchy = "time"
    list_display = ["time_p", "run", "kind", "line_number", "number", "text"]
    list_filter = ["kind", "run__job"]
    readonly_fields = ("time_p", "run", "kind", "line_number", "number", "text")

    time_p = PreciseTimeFormatter(JobRunLogEntry, "time")

    list_per_page = 10
    show_full_result_count = False
    #paginator = Paginator

    def get_changelist(self, request, **kwargs):
        return CustomChangeList
    

@admin.register(JobRunQueueItem)
class JobRunQueueItemAdmin(ReadOnlyAdmin):
    date_hierarchy = "run_at"
    list_display = ["run_at", "scheduled_job", "assigned_at", "assignee_pid"]


@admin.register(ScheduledJob)
class ScheduledJobAdmin(admin.ModelAdmin):
    list_display = [
        "job",
        "enabled",
        "comment",
        "years",
        "months",
        "days_of_month",
        "weekdays",
        "hours",
        "minutes",
        "timezone",
    ]
    list_filter = ["enabled"]


@admin.register(Timezone)
class TimezoneAdmin(admin.ModelAdmin):
    pass
