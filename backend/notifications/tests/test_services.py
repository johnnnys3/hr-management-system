"""`notifications.services.send`, `docs/05-database-schema.md` §3.2. The
create-side entry point every other module is expected to call — no HTTP
create surface exists, so this is exercised directly."""
from unittest.mock import patch

from django.test import TestCase

from iam.roles import HR_OFFICER
from notifications import services
from notifications.models import Notification

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
    def test_send_with_email_channel_dispatches_mail(self, mail_send):
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
    def test_send_with_both_channel_dispatches_mail(self, mail_send):
        services.send(
            recipient=self.recipient,
            category=Notification.CATEGORY_REQUEST_UPDATE,
            channel=Notification.CHANNEL_BOTH,
            subject='Update',
            body='Body text',
        )

        mail_send.assert_called_once()
