from unittest.mock import patch

from django.test import TestCase

from mail import services


class SendTests(TestCase):
    def test_send_queues_the_task_with_given_arguments(self):
        with patch('mail.services.send_mail_task') as task:
            services.send(template='test_email', recipient='a@example.com', context={'x': 1})

        task.delay.assert_called_once_with(
            template='test_email', recipient='a@example.com', context={'x': 1}
        )

    def test_send_defaults_context_to_empty_dict(self):
        with patch('mail.services.send_mail_task') as task:
            services.send(template='test_email', recipient='a@example.com')

        task.delay.assert_called_once_with(
            template='test_email', recipient='a@example.com', context={}
        )
