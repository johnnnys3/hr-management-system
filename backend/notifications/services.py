"""Notification's public API.

Per ADR-0011 and `docs/04-system-architecture.md` §3.2, emission is
cross-cutting and absorbed per consumer: other modules import and call
`send` inside their own `transaction.atomic()` block rather than writing to
`notification` directly or reaching it over HTTP — the same reasoning
`audit.services.record` follows for `audit_log`. When `channel` includes
email, this module is mail dispatch's consumer, not the reverse.
"""
import mail.services

from .models import Notification


def send(*, recipient, category, channel, subject, body, related_type=None, related_id=None):
    notification = Notification.objects.create(
        recipient=recipient,
        category=category,
        channel=channel,
        subject=subject,
        body=body,
        related_type=related_type,
        related_id=related_id,
    )
    if channel in (Notification.CHANNEL_EMAIL, Notification.CHANNEL_BOTH):
        mail.services.send(
            template='notification',
            recipient=recipient.email,
            context={'subject': subject, 'body': body},
        )
    return notification
