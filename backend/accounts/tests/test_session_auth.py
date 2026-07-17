"""ADR-0004: session-cookie login/logout/me. HRMS-NFR-023: inactivity expiry."""
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()

LOGIN_URL = '/api/auth/login/'
LOGOUT_URL = '/api/auth/logout/'
ME_URL = '/api/auth/me/'


class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='alice@example.com', password='correct-password')

    def test_valid_credentials_log_in_and_set_session_cookie(self):
        response = self.client.post(LOGIN_URL, {'email': 'alice@example.com', 'password': 'correct-password'})

        self.assertEqual(response.status_code, 200)
        self.assertIn(settings.SESSION_COOKIE_NAME, response.cookies)
        cookie = response.cookies[settings.SESSION_COOKIE_NAME]
        self.assertEqual(cookie['httponly'], True)
        self.assertEqual(cookie['samesite'], 'Lax')

    def test_valid_credentials_are_case_insensitive_on_email(self):
        response = self.client.post(LOGIN_URL, {'email': 'ALICE@EXAMPLE.COM', 'password': 'correct-password'})

        self.assertEqual(response.status_code, 200)

    def test_wrong_password_is_rejected(self):
        response = self.client.post(LOGIN_URL, {'email': 'alice@example.com', 'password': 'wrong'})

        self.assertEqual(response.status_code, 401)

    def test_unknown_email_is_rejected_with_the_same_response_as_wrong_password(self):
        known = self.client.post(LOGIN_URL, {'email': 'alice@example.com', 'password': 'wrong'})
        unknown = self.client.post(LOGIN_URL, {'email': 'nobody@example.com', 'password': 'wrong'})

        self.assertEqual(known.status_code, unknown.status_code)

    def test_inactive_account_is_rejected(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(LOGIN_URL, {'email': 'alice@example.com', 'password': 'correct-password'})

        self.assertEqual(response.status_code, 401)


class LogoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='alice@example.com', password='correct-password')

    def test_logout_ends_the_session(self):
        self.client.login(email='alice@example.com', password='correct-password')

        self.client.post(LOGOUT_URL)
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, 401)

    def test_logout_requires_authentication(self):
        response = self.client.post(LOGOUT_URL)

        self.assertEqual(response.status_code, 401)


class MeTests(APITestCase):
    def test_returns_caller_identity_and_groups(self):
        user = User.objects.create_user(email='alice@example.com', password='x')
        self.client.force_authenticate(user)

        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'alice@example.com')
        self.assertEqual(response.data['groups'], [])

    def test_anonymous_is_denied(self):
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, 401)


class InactivityExpiryTests(APITestCase):
    def test_session_cookie_age_is_the_configured_inactivity_window(self):
        """HRMS-NFR-023: sessions expire after a defined period of inactivity.
        SESSION_SAVE_EVERY_REQUEST makes this an inactivity window rather
        than a fixed time-since-login, refreshing on each request."""
        self.assertTrue(settings.SESSION_SAVE_EVERY_REQUEST)
        self.assertGreater(settings.SESSION_COOKIE_AGE, 0)
