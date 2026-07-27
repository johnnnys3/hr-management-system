from unittest.mock import patch

from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User


class EmailVerificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='a@example.com', password='x')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @patch('accounts.services.mail.services.send')
    def test_send_stores_hashed_code_and_queues_mail(self, mail_send):
        from accounts.services import send_email_verification

        send_email_verification(self.user)

        self.user.refresh_from_db()
        self.assertIsNone(self.user.email_verified_at)
        self.assertIsNotNone(self.user.email_verification_code_hash)
        mail_send.assert_called_once()
        self.assertEqual(mail_send.call_args.kwargs['template'], 'email_verification')
        self.assertEqual(mail_send.call_args.kwargs['recipient'], self.user.email)

    @patch('accounts.services.mail.services.send')
    def test_confirm_with_correct_code_verifies_email(self, mail_send):
        from accounts.services import send_email_verification

        with patch('accounts.services._generate_code', return_value='123456'):
            send_email_verification(self.user)

        response = self.client.post('/api/auth/email/confirm/', {'code': '123456'}, format='json')

        self.assertEqual(response.status_code, 204)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.email_verified_at)
        self.assertIsNone(self.user.email_verification_code_hash)

    @patch('accounts.services.mail.services.send')
    def test_confirm_with_wrong_code_fails(self, mail_send):
        from accounts.services import send_email_verification

        with patch('accounts.services._generate_code', return_value='123456'):
            send_email_verification(self.user)

        response = self.client.post('/api/auth/email/confirm/', {'code': '000000'}, format='json')

        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.email_verified_at)

    @patch('accounts.services.mail.services.send')
    def test_confirm_after_expiry_fails(self, mail_send):
        from accounts.services import send_email_verification

        with patch('accounts.services._generate_code', return_value='123456'):
            send_email_verification(self.user)
        self.user.email_verification_expires_at = timezone.now() - timezone.timedelta(seconds=1)
        self.user.save(update_fields=['email_verification_expires_at'])

        response = self.client.post('/api/auth/email/confirm/', {'code': '123456'}, format='json')

        self.assertEqual(response.status_code, 400)

    @patch('accounts.services.mail.services.send')
    def test_code_is_never_stored_in_plaintext(self, mail_send):
        from accounts.services import send_email_verification

        with patch('accounts.services._generate_code', return_value='123456'):
            send_email_verification(self.user)

        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email_verification_code_hash, '123456')
        self.assertTrue(check_password('123456', self.user.email_verification_code_hash))


class LoginBlockedUntilEmailVerifiedTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_with_unverified_email_is_pending_not_fully_authenticated(self):
        User.objects.create_user(email='new@example.com', password='x', email_verified_at=None)

        response = self.client.post('/api/auth/login/', {'email': 'new@example.com', 'password': 'x'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['email_verification_required'])
        # Session established (can reach email-confirm/logout) but not
        # fully authenticated — e.g. /api/auth/me/'s own permission is
        # IsAuthenticated so it still works, but an IsFullyAuthenticated-
        # gated endpoint (role-grant-requests GET) must not.
        blocked = self.client.get('/api/role-grant-requests/')
        self.assertEqual(blocked.status_code, 403)

    @patch('accounts.services.mail.services.send')
    def test_confirming_the_code_clears_the_pending_session(self, mail_send):
        user = User.objects.create_user(email='new2@example.com', password='x', email_verified_at=None)
        with patch('accounts.services._generate_code', return_value='123456'):
            from accounts.services import send_email_verification
            send_email_verification(user)
        self.client.post('/api/auth/login/', {'email': 'new2@example.com', 'password': 'x'}, format='json')

        confirm = self.client.post('/api/auth/email/confirm/', {'code': '123456'}, format='json')

        self.assertEqual(confirm.status_code, 204)

    @patch('accounts.services.mail.services.send')
    def test_password_reset_forces_reverification_on_next_login(self, mail_send):
        from accounts.services import confirm_password_reset, request_password_reset
        from django.contrib.auth.tokens import PasswordResetTokenGenerator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        user = User.objects.create_user(email='reset@example.com', password='old')
        self.assertIsNotNone(user.email_verified_at)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)
        ok = confirm_password_reset(uid, token, 'newpassword123')

        self.assertTrue(ok)
        user.refresh_from_db()
        self.assertIsNone(user.email_verified_at)

        response = self.client.post('/api/auth/login/', {'email': 'reset@example.com', 'password': 'newpassword123'}, format='json')
        self.assertTrue(response.data['email_verification_required'])


class UserCreationSendsVerificationTests(TestCase):
    @patch('accounts.services.mail.services.send')
    def test_creating_a_user_sends_verification_email(self, mail_send):
        admin = User.objects.create_user(email='admin@example.com', password='x')
        from django.contrib.auth.models import Group
        admin.groups.add(Group.objects.get(name='System Administrator'))
        client = APIClient()
        client.force_authenticate(admin)

        response = client.post('/api/users/', {'email': 'new@example.com', 'password': 'x'}, format='json')

        self.assertEqual(response.status_code, 201)
        mail_send.assert_called_once()
        self.assertEqual(mail_send.call_args.kwargs['template'], 'email_verification')
        new_user = User.objects.get(email='new@example.com')
        self.assertIsNone(new_user.email_verified_at)
        self.assertIsNotNone(new_user.email_verification_code_hash)
