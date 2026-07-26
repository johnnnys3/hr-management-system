"""Notification's public API.

Per ADR-0011 and `docs/04-system-architecture.md` §3.2, emission is
cross-cutting and absorbed per consumer: other modules import and call
`send` inside their own `transaction.atomic()` block rather than writing to
`notification` directly or reaching it over HTTP — the same reasoning
`audit.services.record` follows for `audit_log`. When `channel` includes
email, this module is mail dispatch's consumer, not the reverse.

SMS resolution (docs/superpowers/specs/2026-07-26-notifications-email-sms-design.md
§6): SMS rides on the same channel ceiling as email — no caller passes a
channel that means "SMS but not email." A caller's existing `channel`
argument is unchanged in meaning; this module decides, per recipient, which
of the callee's allowed channels actually go out, gated on preference,
verified phone, and the daily rate cap (§7).
"""
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

import mail.services
import sms.services

from .models import Notification, NotificationPreference


def _reserve_sms_quota(user):
    """Atomically reserve one SMS quota slot. Returns True if quota was
    reserved successfully, False if the daily cap was already reached. This
    must be called BEFORE enqueueing or sending the message to prevent
    concurrent requests from exceeding SMS_DAILY_CAP_PER_USER."""
    key = f'sms:count:{user.pk}:{timezone.now().date().isoformat()}'
    tomorrow = timezone.now().date() + timezone.timedelta(days=1)
    midnight = timezone.make_aware(timezone.datetime.combine(tomorrow, timezone.datetime.min.time()))
    ttl = max(int((midnight - timezone.now()).total_seconds()), 1)

    try:
        new_count = cache.incr(key)
    except ValueError:
        # Key doesn't exist yet today — first SMS of the day for this user.
        cache.set(key, 1, timeout=ttl)
        new_count = 1

    return new_count <= settings.SMS_DAILY_CAP_PER_USER


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
    channel_allows_email = channel in (Notification.CHANNEL_EMAIL, Notification.CHANNEL_BOTH)
    if channel_allows_email:
        preference, _ = NotificationPreference.objects.get_or_create(user=recipient)

        if preference.email_enabled:
            # Deferred to commit: `mail.services.send` only enqueues a Celery
            # task, off the transaction entirely — queuing it immediately would
            # dispatch mail for a notification (or its wider caller) that a
            # later rollback undoes.
            transaction.on_commit(
                lambda: mail.services.send(
                    template='notification',
                    recipient=recipient.email,
                    context={'subject': subject, 'body': body},
                )
            )

        if preference.sms_enabled and recipient.phone_verified_at is not None:
            def _send_sms():
                if not _reserve_sms_quota(recipient):
                    return
                sms.services.send(to=recipient.phone_number, body=f'{subject}: {body}')

            transaction.on_commit(_send_sms)

    return notification
