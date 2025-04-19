from django.core.management.base import BaseCommand
from apscheduler.schedulers.blocking import BlockingScheduler
from fraud.emails_send import send_fraud_alerts_emails

class Command(BaseCommand):
    help = "fraud email scheduler."

    def handle(self, *args, **kwargs):
        print("Email scheduler started.")
        scheduler = BlockingScheduler()
        scheduler.add_job(send_fraud_alerts_emails, "interval", minutes=2)
        try:
            scheduler.start()
        except KeyboardInterrupt:
            print("Email scheduler stopped.")

