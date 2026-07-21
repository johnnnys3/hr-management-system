"""ADR-0004: session-cookie login/logout/me. HRMS-NFR-023: inactivity expiry."""
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

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
        self.assertEqual(bool(cookie['secure']), settings.SESSION_COOKIE_SECURE)

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

    def test_login_without_a_csrf_token_is_rejected(self):
        """Login-CSRF: without this, a page under attacker control could
        force a victim's browser to authenticate as the attacker's account."""
        strict_client = APIClient(enforce_csrf_checks=True)

        response = strict_client.post(LOGIN_URL, {'email': 'alice@example.com', 'password': 'correct-password'})

        self.assertEqual(response.status_code, 403)

    def test_login_with_a_valid_csrf_token_succeeds(self):
        strict_client = APIClient(enforce_csrf_checks=True)
        strict_client.get('/api/auth/csrf/')
        csrf_token = strict_client.cookies[settings.CSRF_COOKIE_NAME].value

        response = strict_client.post(
            LOGIN_URL, {'email': 'alice@example.com', 'password': 'correct-password'},
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(response.status_code, 200)


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

    def test_derived_roles_are_false_with_no_employee_record(self):
        user = User.objects.create_user(email='noemployee@example.com', password='x')
        self.client.force_authenticate(user)

        response = self.client.get(ME_URL)

        self.assertFalse(response.data['is_employee'])
        self.assertFalse(response.data['is_manager'])

    def test_derived_roles_reflect_employee_and_manager_status(self):
        from leave.tests.helpers import make_manager_and_report

        manager, report = make_manager_and_report()
        manager_user = User.objects.create_user(email='manager@example.com', password='x', employee=manager)
        report_user = User.objects.create_user(email='report@example.com', password='x', employee=report)

        self.client.force_authenticate(manager_user)
        manager_response = self.client.get(ME_URL)
        self.assertTrue(manager_response.data['is_employee'])
        self.assertTrue(manager_response.data['is_manager'])

        self.client.force_authenticate(report_user)
        report_response = self.client.get(ME_URL)
        self.assertTrue(report_response.data['is_employee'])
        self.assertFalse(report_response.data['is_manager'])


class InactivityExpiryTests(APITestCase):
    def test_session_cookie_age_is_the_configured_inactivity_window(self):
        """HRMS-NFR-023: sessions expire after a defined period of inactivity.
        SESSION_SAVE_EVERY_REQUEST makes this an inactivity window rather
        than a fixed time-since-login, refreshing on each request."""
        self.assertTrue(settings.SESSION_SAVE_EVERY_REQUEST)
        self.assertGreater(settings.SESSION_COOKIE_AGE, 0)
