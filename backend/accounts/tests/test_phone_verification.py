from unittest.mock import patch

from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User


class PhoneVerificationRequestTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='a@example.com', password='x')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @patch('accounts.services.sms.services.send')
    def test_request_stores_hashed_code_and_sends_sms(self, sms_send):
        response = self.client.post('/api/auth/phone/', {'phone_number': '+15559998888'}, format='json')

        self.assertEqual(response.status_code, 202)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, '+15559998888')
        self.assertIsNone(self.user.phone_verified_at)
        self.assertIsNotNone(self.user.phone_verification_code_hash)
        self.assertIsNotNone(self.user.phone_verification_expires_at)
        sms_send.assert_called_once()
        self.assertEqual(sms_send.call_args.kwargs['to'], '+15559998888')

    @patch('accounts.services.sms.services.send')
    def test_requesting_a_new_number_clears_prior_verification(self, sms_send):
        self.user.phone_number = '+15551110000'
        self.user.phone_verified_at = timezone.now()
        self.user.save(update_fields=['phone_number', 'phone_verified_at'])

        self.client.post('/api/auth/phone/', {'phone_number': '+15559998888'}, format='json')

        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, '+15559998888')
        self.assertIsNone(self.user.phone_verified_at)

    def test_anonymous_cannot_request(self):
        anon_client = APIClient()
        response = anon_client.post('/api/auth/phone/', {'phone_number': '+15559998888'}, format='json')
        self.assertEqual(response.status_code, 401)


class PhoneVerificationConfirmTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='a@example.com', password='x')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @patch('accounts.services.sms.services.send')
    def test_confirm_with_correct_code_verifies_phone(self, sms_send):
        with patch('accounts.services._generate_code', return_value='123456'):
            self.client.post('/api/auth/phone/', {'phone_number': '+15559998888'}, format='json')

        response = self.client.post('/api/auth/phone/confirm/', {'code': '123456'}, format='json')

        self.assertEqual(response.status_code, 204)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.phone_verified_at)
        self.assertIsNone(self.user.phone_verification_code_hash)

    @patch('accounts.services.sms.services.send')
    def test_confirm_with_wrong_code_fails_generically(self, sms_send):
        with patch('accounts.services._generate_code', return_value='123456'):
            self.client.post('/api/auth/phone/', {'phone_number': '+15559998888'}, format='json')

        response = self.client.post('/api/auth/phone/confirm/', {'code': '000000'}, format='json')

        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.phone_verified_at)

    @patch('accounts.services.sms.services.send')
    def test_confirm_after_expiry_fails(self, sms_send):
        with patch('accounts.services._generate_code', return_value='123456'):
            self.client.post('/api/auth/phone/', {'phone_number': '+15559998888'}, format='json')
        self.user.refresh_from_db()
        self.user.phone_verification_expires_at = timezone.now() - timezone.timedelta(seconds=1)
        self.user.save(update_fields=['phone_verification_expires_at'])

        response = self.client.post('/api/auth/phone/confirm/', {'code': '123456'}, format='json')

        self.assertEqual(response.status_code, 400)

    def test_code_is_never_stored_in_plaintext(self):
        with patch('accounts.services.sms.services.send'), \
             patch('accounts.services._generate_code', return_value='123456'):
            self.client.post('/api/auth/phone/', {'phone_number': '+15559998888'}, format='json')

        self.user.refresh_from_db()
        self.assertNotEqual(self.user.phone_verification_code_hash, '123456')
        self.assertTrue(check_password('123456', self.user.phone_verification_code_hash))
