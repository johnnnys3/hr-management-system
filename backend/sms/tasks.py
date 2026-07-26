# backend/sms/tasks.py
"""The Celery task that sends SMS off the request cycle.

Mirrors `mail.tasks.send_mail_task` (ADR-0011): delivery is best-effort, the
domain action that queued this has already committed, and a delivery
failure must not undo it. Retry is bounded, and exhausting it logs to the
application log — never to `audit_log`.
"""
import logging

from celery import shared_task
from django.conf import settings
from twilio.rest import Client

logger = logging.getLogger('sms')

MAX_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 60


def _twilio_client():
    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def _masked(number):
    """Last 2 digits visible, rest redacted — enough to spot a stuck number
    without writing a full phone number to a log with no access control."""
    if len(number) < 2:
        return '***'
    return f'***{number[-2:]}'


@shared_task(bind=True, max_retries=MAX_ATTEMPTS - 1)
def send_sms_task(self, *, to, body):
    try:
        _twilio_client().messages.create(to=to, from_=settings.TWILIO_FROM_NUMBER, body=body)
    except Exception as exc:
        if self.request.retries >= MAX_ATTEMPTS - 1:
            logger.error(
                'sms dispatch: giving up on sending to %s after %s attempts: %s',
                _masked(to), self.request.retries + 1, type(exc).__name__,
            )
            return
        raise self.retry(exc=exc, countdown=RETRY_BACKOFF_SECONDS * (2 ** self.request.retries))
