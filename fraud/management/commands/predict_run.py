import time
from django.core.management.base import BaseCommand
from fraud.predictscheduler import start_schedular
class Command(BaseCommand):
    help = "fraud detection."
    def handle(self, *args, **kwargs):
        print("Starting fraud prediction scheduler.")
        start_schedular()
        try:
            while True:
                time.sleep(10)
        except (KeyboardInterrupt, SystemExit):
            print("Fraud prediction scheduler stopped.")
