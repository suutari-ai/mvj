import os
import time
from datetime import timedelta
from typing import NoReturn

from django.db import transaction

from ._times import utc_now
from .models import JobRunQueueItem
from .job_launching import run_job

POLL_INTERVAL = 10.0  # seconds
SKIP_PAST_ITEMS_OLDER_THAN = timedelta(minutes=5)


def run_scheduler_loop() -> NoReturn:
    queue_items = JobRunQueueItem.objects.filter(
        scheduled_job__enabled=True,
        assigned_at=None).order_by('run_at')

    while True:
        # Remove old queue items
        oldest_runnable = utc_now() - SKIP_PAST_ITEMS_OLDER_THAN
        queue_items.filter(run_at__lt=oldest_runnable).delete()

        first_item = queue_items.first()
        if not first_item:
            # Nothing in the queue, check again after poll interval
            time.sleep(POLL_INTERVAL)
            continue

        secs_to_first = (first_item.run_at - utc_now()).total_seconds()

        if secs_to_first > POLL_INTERVAL:
            # Let's check the queue again after poll interval, since a
            # new first item could be added mean while
            time.sleep(POLL_INTERVAL)
            continue

        time.sleep(max(secs_to_first, 0.0))

        with transaction.atomic():
            locked_item = (
                queue_items.filter(pk=first_item.pk)
                .select_for_update(skip_locked=True)
                .first())

            if not locked_item:
                # Someone else picked it up already
                continue

            # Assign the item for us
            locked_item.assigned_at = utc_now()
            locked_item.assignee_pid = os.getpid()
            locked_item.save(update_fields=['assigned_at', 'assignee_pid'])

        run_job(first_item.scheduled_job.job)

        first_item.scheduled_job.update_run_queue()
