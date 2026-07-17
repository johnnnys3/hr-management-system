"""ADR-0011: password reset consumes mail dispatch directly. Uniform
response regardless of address existence or send success (enumeration-oracle
prevention)."""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.test import APITestCase

from accounts.services import password_reset_token_generator

User = get_user_model()

REQUEST_URL = '/api/auth/password-reset/'
CONFIRM_URL = '/api/auth/password-reset/confirm/'


class PasswordResetRequestTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='alice@example.com', password='old-password')

    def test_known_address_gets_202_and_queues_mail_dispatch(self):
        with patch('accounts.services.mail.services.send') as send:
            response = self.client.post(REQUEST_URL, {'email': 'alice@example.com'})

        self.assertEqual(response.status_code, 202)
        send.assert_called_once()
        self.assertEqual(send.call_args.kwargs['template'], 'password_reset')
        self.assertEqual(send.call_args.kwargs['recipient'], 'alice@example.com')

    def test_unknown_address_gets_the_same_202_and_sends_nothing(self):
        with patch('accounts.services.mail.services.send') as send:
            response = self.client.post(REQUEST_URL, {'email': 'nobody@example.com'})

        self.assertEqual(response.status_code, 202)
        send.assert_not_called()

    def test_inactive_account_gets_the_same_202_and_sends_nothing(self):
        self.user.is_active = False
        self.user.save()

        with patch('accounts.services.mail.services.send') as send:
            response = self.client.post(REQUEST_URL, {'email': 'alice@example.com'})

        self.assertEqual(response.status_code, 202)
        send.assert_not_called()


class PasswordResetConfirmTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='alice@example.com', password='old-password')
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = password_reset_token_generator.make_token(self.user)

    def test_valid_token_sets_the_new_password(self):
        response = self.client.post(CONFIRM_URL, {
            'uid': self.uid, 'token': self.token, 'password': 'brand-new-password',
        })

        self.assertEqual(response.status_code, 204)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('brand-new-password'))

    def test_reused_token_is_rejected(self):
        self.client.post(CONFIRM_URL, {'uid': self.uid, 'token': self.token, 'password': 'first-new-password'})

        response = self.client.post(CONFIRM_URL, {
            'uid': self.uid, 'token': self.token, 'password': 'second-new-password',
        })

        self.assertEqual(response.status_code, 400)

    def test_invalid_token_is_rejected(self):
        response = self.client.post(CONFIRM_URL, {
            'uid': self.uid, 'token': 'not-a-real-token', 'password': 'brand-new-password',
        })

        self.assertEqual(response.status_code, 400)

    def test_garbage_uid_is_rejected_not_500(self):
        response = self.client.post(CONFIRM_URL, {
            'uid': 'not-base64', 'token': self.token, 'password': 'brand-new-password',
        })

        self.assertEqual(response.status_code, 400)
