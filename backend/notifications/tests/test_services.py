"""`notifications.services.send`, `docs/05-database-schema.md` §3.2. The
create-side entry point every other module is expected to call — no HTTP
create surface exists, so this is exercised directly."""
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone

from iam.roles import HR_OFFICER
from notifications import services
from notifications.models import Notification, NotificationPreference

from .helpers import user_with_role


class SendTests(TestCase):
    def setUp(self):
        self.recipient = user_with_role('recipient@example.com', HR_OFFICER)

    def test_send_creates_an_in_app_notification(self):
        notification = services.send(
            recipient=self.recipient,
            category=Notification.CATEGORY_PENDING_TASK,
            channel=Notification.CHANNEL_IN_APP,
            subject='A task is waiting',
            body='Please review requisition #4.',
            related_type='job_requisition',
            related_id=4,
        )

        self.assertEqual(notification.recipient, self.recipient)
        self.assertEqual(notification.category, Notification.CATEGORY_PENDING_TASK)
        self.assertEqual(notification.channel, Notification.CHANNEL_IN_APP)
        self.assertIsNone(notification.read_at)
        self.assertEqual(Notification.objects.count(), 1)

    @patch('mail.services.send')
    def test_send_with_in_app_channel_does_not_dispatch_mail(self, mail_send):
        services.send(
            recipient=self.recipient,
            category=Notification.CATEGORY_REQUEST_UPDATE,
            channel=Notification.CHANNEL_IN_APP,
            subject='Update',
            body='Body',
        )

        mail_send.assert_not_called()

    @patch('mail.services.send')
    def test_send_with_email_channel_dispatches_mail_on_commit(self, mail_send):
        with self.captureOnCommitCallbacks(execute=True):
            services.send(
                recipient=self.recipient,
                category=Notification.CATEGORY_REQUEST_UPDATE,
                channel=Notification.CHANNEL_EMAIL,
                subject='Update',
                body='Body text',
            )

        mail_send.assert_called_once_with(
            template='notification', recipient=self.recipient.email, context={'subject': 'Update', 'body': 'Body text'},
        )

    @patch('mail.services.send')
    def test_send_with_both_channel_dispatches_mail_on_commit(self, mail_send):
        with self.captureOnCommitCallbacks(execute=True):
            services.send(
                recipient=self.recipient,
                category=Notification.CATEGORY_REQUEST_UPDATE,
                channel=Notification.CHANNEL_BOTH,
                subject='Update',
                body='Body text',
            )

        mail_send.assert_called_once()

    @patch('mail.services.send')
    def test_send_with_email_channel_does_not_dispatch_before_commit(self, mail_send):
        services.send(
            recipient=self.recipient,
            category=Notification.CATEGORY_REQUEST_UPDATE,
            channel=Notification.CHANNEL_EMAIL,
            subject='Update',
            body='Body text',
        )

        mail_send.assert_not_called()


class SmsResolutionTests(TestCase):
    def setUp(self):
        self.recipient = user_with_role('sms-recipient@example.com', HR_OFFICER)
        cache.clear()

    def _verify_phone(self):
        self.recipient.phone_number = '+15559998888'
        self.recipient.phone_verified_at = timezone.now()
        self.recipient.save(update_fields=['phone_number', 'phone_verified_at'])

    @patch('sms.services.send')
    @patch('mail.services.send')
    def test_sms_not_sent_when_preference_disabled(self, mail_send, sms_send):
        self._verify_phone()
        NotificationPreference.objects.create(user=self.recipient, sms_enabled=False)

        with self.captureOnCommitCallbacks(execute=True):
            services.send(
                recipient=self.recipient, category=Notification.CATEGORY_REQUEST_UPDATE,
                channel=Notification.CHANNEL_BOTH, subject='S', body='B',
            )

        sms_send.assert_not_called()

    @patch('sms.services.send')
    @patch('mail.services.send')
    def test_sms_not_sent_when_phone_unverified(self, mail_send, sms_send):
        NotificationPreference.objects.create(user=self.recipient, sms_enabled=True)

        with self.captureOnCommitCallbacks(execute=True):
            services.send(
                recipient=self.recipient, category=Notification.CATEGORY_REQUEST_UPDATE,
                channel=Notification.CHANNEL_BOTH, subject='S', body='B',
            )

        sms_send.assert_not_called()

    @patch('sms.services.send')
    @patch('mail.services.send')
    def test_sms_sent_when_enabled_verified_and_channel_includes_email(self, mail_send, sms_send):
        self._verify_phone()
        NotificationPreference.objects.create(user=self.recipient, sms_enabled=True)

        with self.captureOnCommitCallbacks(execute=True):
            services.send(
                recipient=self.recipient, category=Notification.CATEGORY_REQUEST_UPDATE,
                channel=Notification.CHANNEL_BOTH, subject='S', body='B',
            )

        sms_send.assert_called_once_with(to='+15559998888', body='S: B')

    @patch('sms.services.send')
    @patch('mail.services.send')
    def test_sms_not_sent_when_channel_is_in_app_only(self, mail_send, sms_send):
        self._verify_phone()
        NotificationPreference.objects.create(user=self.recipient, sms_enabled=True)

        with self.captureOnCommitCallbacks(execute=True):
            services.send(
                recipient=self.recipient, category=Notification.CATEGORY_REQUEST_UPDATE,
                channel=Notification.CHANNEL_IN_APP, subject='S', body='B',
            )

        sms_send.assert_not_called()

    @patch('sms.services.send')
    @patch('mail.services.send')
    @override_settings(SMS_DAILY_CAP_PER_USER=2)
    def test_sms_stops_after_daily_cap_reached(self, mail_send, sms_send):
        self._verify_phone()
        NotificationPreference.objects.create(user=self.recipient, sms_enabled=True)

        with self.captureOnCommitCallbacks(execute=True):
            for _ in range(3):
                services.send(
                    recipient=self.recipient, category=Notification.CATEGORY_REQUEST_UPDATE,
                    channel=Notification.CHANNEL_BOTH, subject='S', body='B',
                )

        self.assertEqual(sms_send.call_count, 2)
