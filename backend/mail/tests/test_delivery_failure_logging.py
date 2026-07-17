"""ADR-0011: delivery failure goes to application logs, never audit_log."""
from unittest.mock import patch

from django.test import TestCase, override_settings

from audit.models import AuditLog
from mail.tasks import send_mail_task


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class DeliveryFailureDoesNotTouchAuditLogTests(TestCase):
    def test_exhausted_retries_write_no_audit_log_entry(self):
        with patch(
            'mail.tasks.EmailMultiAlternatives.send',
            side_effect=ConnectionError('smtp unreachable'),
        ), patch('mail.tasks.RETRY_BACKOFF_SECONDS', 0):
            with self.assertLogs('mail', level='ERROR'):
                send_mail_task.delay(
                    template='test_email', recipient='x@example.com', context={}
                )

        self.assertEqual(AuditLog.objects.count(), 0)
