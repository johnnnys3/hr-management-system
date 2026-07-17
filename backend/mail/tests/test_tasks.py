import smtplib
from unittest.mock import patch

from django.core import mail
from django.template import TemplateDoesNotExist
from django.test import TestCase, override_settings

from mail.tasks import MAX_ATTEMPTS, send_mail_task


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

        self.assertEqual(send.call_count, MAX_ATTEMPTS)
        self.assertTrue(result.successful())
        self.assertTrue(any('giving up' in message for message in logs.output))

    def test_giving_up_log_masks_the_recipient_address(self):
        with patch(
            'mail.tasks.EmailMultiAlternatives.send',
            side_effect=ConnectionError('smtp unreachable'),
        ), patch('mail.tasks.RETRY_BACKOFF_SECONDS', 0):
            with self.assertLogs('mail', level='ERROR') as logs:
                send_mail_task.delay(
                    template='test_email', recipient='someone@example.com', context={}
                )

        self.assertTrue(any('giving up' in message for message in logs.output))
        self.assertTrue(any('s***@example.com' in message for message in logs.output))
        self.assertFalse(any('someone@example.com' in message for message in logs.output))

    def test_giving_up_log_does_not_leak_the_address_via_the_exception_text(self):
        """SMTPRecipientsRefused embeds the rejected address in str(exc);
        logging the exception itself would defeat _masked(recipient)."""
        refused = smtplib.SMTPRecipientsRefused(
            {'someone@example.com': (550, b'5.1.1 User unknown')}
        )
        with patch(
            'mail.tasks.EmailMultiAlternatives.send', side_effect=refused
        ), patch('mail.tasks.RETRY_BACKOFF_SECONDS', 0):
            with self.assertLogs('mail', level='ERROR') as logs:
                send_mail_task.delay(
                    template='test_email', recipient='someone@example.com', context={}
                )

        self.assertFalse(any('someone@example.com' in message for message in logs.output))
        self.assertTrue(any('SMTPRecipientsRefused' in message for message in logs.output))

    @override_settings(CELERY_TASK_EAGER_PROPAGATES=True)
    def test_a_broken_template_fails_fast_without_retrying(self):
        with patch(
            'mail.tasks.render', side_effect=TemplateDoesNotExist('mail/nope')
        ) as render:
            with self.assertRaises(TemplateDoesNotExist):
                send_mail_task.delay(
                    template='nope', recipient='x@example.com', context={}
                )

        render.assert_called_once_with('nope', {})
