"""Throwaway command for /verify — module 2 has no real callers yet.

Sends the `test_email` template through the same Celery task and SMTP
configuration a future consumer would use, so delivery can be confirmed
against a local catcher (e.g. Mailpit) without waiting for Authentication,
Onboarding, Notification, or Payroll to exist.
"""
from datetime import datetime, timezone

from django.core.management.base import BaseCommand

from mail import services


class Command(BaseCommand):
    help = 'Sends a test email through mail dispatch to confirm end-to-end delivery.'

    def add_arguments(self, parser):
        parser.add_argument('--to', required=True, help='Recipient address')

    def handle(self, *args, **options):
        services.send(
            template='test_email',
            recipient=options['to'],
            context={'sent_at': datetime.now(timezone.utc).isoformat()},
        )
        self.stdout.write(self.style.SUCCESS(f"Queued test email to {options['to']}"))
