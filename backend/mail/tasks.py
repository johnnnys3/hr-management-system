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

MAX_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 60


def _masked(recipient):
    """Local-part masked, domain intact — enough to spot a stuck mailbox
    without writing a full address to a log with no access control."""
    local, _, domain = recipient.partition('@')
    if not domain:
        return '***'
    return f'{local[:1]}***@{domain}'


@shared_task(bind=True, max_retries=MAX_ATTEMPTS - 1)
def send_mail_task(self, *, template, recipient, context):
    # Rendering is a template bug, not a delivery failure: TemplateDoesNotExist
    # or a syntax error should fail loudly, not retry three times and then
    # get logged as if the mailbox were unreachable.
    subject, text_body, html_body = render(template, context)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    if html_body is not None:
        message.attach_alternative(html_body, 'text/html')

    try:
        message.send()
    except Exception as exc:
        if self.request.retries >= MAX_ATTEMPTS - 1:
            # Exception type only, never str(exc): SMTPRecipientsRefused (and
            # others) embed the rejected address in their message text, which
            # would leak the very recipient _masked() exists to hide.
            logger.error(
                'mail dispatch: giving up on %s to %s after %s attempts: %s',
                template, _masked(recipient), self.request.retries + 1,
                type(exc).__name__,
            )
            return
        raise self.retry(exc=exc, countdown=RETRY_BACKOFF_SECONDS * (2 ** self.request.retries))
