from django.core.management.base import BaseCommand

from ...scheduler import run_scheduler_loop


class Command(BaseCommand):
    help = 'Batch Run Scheduler'

    def handle(self, *args, **options):
        run_scheduler_loop()
