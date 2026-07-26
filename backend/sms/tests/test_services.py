from unittest.mock import patch

from django.test import TestCase

from sms import services


class SendTests(TestCase):
    def test_send_queues_the_task_with_given_arguments(self):
        with patch('sms.services.send_sms_task') as task:
            services.send(to='+15551234567', body='Your code is 123456')

        task.delay.assert_called_once_with(to='+15551234567', body='Your code is 123456')
