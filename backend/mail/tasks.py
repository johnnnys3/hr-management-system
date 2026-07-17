"""The Celery task that sends email off the request cycle.

Delivery is best-effort per ADR-0011: the domain action that queued this
task has already committed, and a delivery failure must not undo it. Retry
is bounded, and exhausting it logs to the application log — never to
`audit_log`, whose categories are fixed by HRMS-NFR-022 and do not extend
to delivery telemetry.
"""
import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from .rendering import render

logger = logging.getLogger('mail')

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 60


@shared_task(bind=True, max_retries=MAX_RETRIES)
def send_mail_task(self, *, template, recipient, context):
    try:
        subject, text_body, html_body = render(template, context)
        message = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        if html_body is not None:
            message.attach_alternative(html_body, 'text/html')
        message.send()
    except Exception as exc:
        if self.request.retries >= MAX_RETRIES:
            logger.error(
                'mail dispatch: giving up on %s to %s after %s retries: %s',
                template, recipient, self.request.retries, exc,
            )
            return
        raise self.retry(exc=exc, countdown=RETRY_BACKOFF_SECONDS * (2 ** self.request.retries))
