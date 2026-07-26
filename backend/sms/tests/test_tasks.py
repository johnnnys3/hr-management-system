from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from sms.tasks import MAX_ATTEMPTS, send_sms_task


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, TWILIO_FROM_NUMBER='+15550001111')
class SendSmsTaskTests(TestCase):
    def test_sends_via_twilio_client(self):
        mock_client = MagicMock()
        with patch('sms.tasks._twilio_client', return_value=mock_client):
            send_sms_task.delay(to='+15559998888', body='Your code is 123456')

        mock_client.messages.create.assert_called_once_with(
            to='+15559998888', from_='+15550001111', body='Your code is 123456',
        )

    def test_retries_on_send_failure_then_gives_up_without_raising(self):
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = ConnectionError('twilio unreachable')
        with patch('sms.tasks._twilio_client', return_value=mock_client), \
             patch('sms.tasks.RETRY_BACKOFF_SECONDS', 0):
            with self.assertLogs('sms', level='ERROR') as logs:
                result = send_sms_task.delay(to='+15559998888', body='Your code is 123456')

        self.assertTrue(result.successful())
        self.assertEqual(mock_client.messages.create.call_count, MAX_ATTEMPTS)
        self.assertIn('giving up', logs.output[0])
        # Number is masked, not logged in full.
        self.assertNotIn('+15559998888', logs.output[0])

    def test_masked_number_keeps_last_two_digits(self):
        from sms.tasks import _masked
        self.assertEqual(_masked('+15559998888'), '***88')

    @override_settings(TWILIO_ACCOUNT_SID='AC123', TWILIO_AUTH_TOKEN='secret')
    def test_twilio_client_is_built_with_a_bounded_timeout(self):
        from sms.tasks import TWILIO_HTTP_TIMEOUT_SECONDS, _twilio_client

        with patch('sms.tasks.Client') as mock_client_cls, patch('sms.tasks.TwilioHttpClient') as mock_http_cls:
            _twilio_client()

        mock_http_cls.assert_called_once_with(timeout=TWILIO_HTTP_TIMEOUT_SECONDS)
        mock_client_cls.assert_called_once_with('AC123', 'secret', http_client=mock_http_cls.return_value)
