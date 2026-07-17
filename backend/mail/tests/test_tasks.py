from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings

from mail.tasks import MAX_RETRIES, send_mail_task


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    CELERY_TASK_ALWAYS_EAGER=True,
)
class SendMailTaskTests(TestCase):
    def test_sends_rendered_template(self):
        send_mail_task.delay(
            template='test_email',
            recipient='someone@example.com',
            context={'sent_at': '2026-07-17T00:00:00+00:00'},
        )

        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.to, ['someone@example.com'])
        self.assertEqual(sent.subject, 'HRMS mail dispatch test')
        self.assertIn('2026-07-17T00:00:00+00:00', sent.body)

    def test_retries_on_send_failure_then_gives_up_without_raising(self):
        with patch(
            'mail.tasks.EmailMultiAlternatives.send',
            side_effect=ConnectionError('smtp unreachable'),
        ) as send, patch('mail.tasks.RETRY_BACKOFF_SECONDS', 0):
            with self.assertLogs('mail', level='ERROR') as logs:
                result = send_mail_task.delay(
                    template='test_email', recipient='x@example.com', context={}
                )

        self.assertEqual(send.call_count, MAX_RETRIES + 1)
        self.assertTrue(result.successful())
        self.assertTrue(any('giving up' in message for message in logs.output))
