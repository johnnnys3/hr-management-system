"""HRMS-NFR-024, ADR-0012 (TOTP): self-enrolment only, presentation on every
authentication for administrators and payroll users."""
import pyotp
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

from accounts import totp
from accounts.models import SecondFactor

User = get_user_model()

LOGIN_URL = '/api/auth/login/'
SECOND_FACTOR_URL = '/api/auth/second-factor/'


def _in_group(email, group_name, password='correct-password'):
    user = User.objects.create_user(email=email, password=password)
    group, _ = Group.objects.get_or_create(name=group_name)
    user.groups.add(group)
    return user


class EnrollmentTests(APITestCase):
    def test_authenticated_user_can_enroll_their_own_factor(self):
        user = User.objects.create_user(email='alice@example.com', password='x')
        self.client.force_authenticate(user)

        response = self.client.post(SECOND_FACTOR_URL)

        self.assertEqual(response.status_code, 201)
        self.assertIn('provisioning_uri', response.data)
        self.assertTrue(SecondFactor.objects.filter(user=user).exists())

    def test_cannot_enroll_twice(self):
        user = User.objects.create_user(email='alice@example.com', password='x')
        self.client.force_authenticate(user)
        self.client.post(SECOND_FACTOR_URL)

        response = self.client.post(SECOND_FACTOR_URL)

        self.assertEqual(response.status_code, 409)

    def test_anonymous_cannot_enroll(self):
        response = self.client.post(SECOND_FACTOR_URL)

        self.assertEqual(response.status_code, 401)

    def test_enrollment_endpoint_has_no_way_to_name_another_user(self):
        """HRMS-NFR-024: 'enrollment shall be performed by the account
        holder' — there is no request field that could target someone else."""
        user = User.objects.create_user(email='alice@example.com', password='x')
        self.client.force_authenticate(user)

        response = self.client.post(SECOND_FACTOR_URL, {'user_id': 9999})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(SecondFactor.objects.get().user, user)

    def test_secret_is_encrypted_at_rest(self):
        user = User.objects.create_user(email='alice@example.com', password='x')
        self.client.force_authenticate(user)

        response = self.client.post(SECOND_FACTOR_URL)

        stored = SecondFactor.objects.get(user=user).secret_ref
        provisioning_uri = response.data['provisioning_uri']
        self.assertNotIn(stored, provisioning_uri)

    def test_re_enrolling_a_disabled_factor_reactivates_the_same_row_not_a_duplicate(self):
        """A OneToOneField: a bare create() on top of an existing disabled
        row would raise IntegrityError rather than ever reach a 201."""
        from django.utils import timezone
        user = User.objects.create_user(email='alice@example.com', password='x')
        SecondFactor.objects.create(
            user=user, secret_ref=totp.encrypt_secret(totp.generate_secret()), disabled_at=timezone.now(),
        )
        self.client.force_authenticate(user)

        response = self.client.post(SECOND_FACTOR_URL)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(SecondFactor.objects.filter(user=user).count(), 1)
        second_factor = SecondFactor.objects.get(user=user)
        self.assertIsNone(second_factor.disabled_at)


class LoginWithSecondFactorTests(APITestCase):
    def test_privileged_role_without_enrollment_logs_in_and_is_told_to_enroll(self):
        """Enrolment (`/api/auth/second-factor/`) is self-service and itself
        requires a session, so the first credential-valid login for an
        account with no factor yet must establish one rather than deadlock."""
        _in_group('admin@example.com', 'System Administrator')

        response = self.client.post(LOGIN_URL, {'email': 'admin@example.com', 'password': 'correct-password'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('second_factor_enrollment_required'))
        self.assertIn('sessionid', response.cookies)

    def test_privileged_role_with_correct_password_but_no_code_is_told_a_factor_is_required(self):
        user = _in_group('payroll@example.com', 'Payroll Officer')
        SecondFactor.objects.create(user=user, secret_ref=totp.encrypt_secret(totp.generate_secret()))

        response = self.client.post(LOGIN_URL, {'email': 'payroll@example.com', 'password': 'correct-password'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('second_factor_required'))
        self.assertNotIn('sessionid', response.cookies)

    def test_privileged_role_with_valid_code_logs_in(self):
        user = _in_group('payroll@example.com', 'Payroll Officer')
        secret = totp.generate_secret()
        SecondFactor.objects.create(user=user, secret_ref=totp.encrypt_secret(secret))
        code = pyotp.TOTP(secret).now()

        response = self.client.post(LOGIN_URL, {
            'email': 'payroll@example.com', 'password': 'correct-password', 'totp_code': code,
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('sessionid', response.cookies)

    def test_privileged_role_with_wrong_code_is_rejected(self):
        user = _in_group('payroll@example.com', 'Payroll Officer')
        SecondFactor.objects.create(user=user, secret_ref=totp.encrypt_secret(totp.generate_secret()))

        response = self.client.post(LOGIN_URL, {
            'email': 'payroll@example.com', 'password': 'correct-password', 'totp_code': '000000',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('second_factor_required'))

    def test_disabled_factor_is_treated_as_needing_enrollment_not_rejected(self):
        """A factor disabled by an approved recovery (§ recovery flow) is
        the same state as never having enrolled: nothing to present, so the
        account holder must be let in to re-enrol."""
        from django.utils import timezone
        user = _in_group('payroll@example.com', 'Payroll Officer')
        SecondFactor.objects.create(
            user=user, secret_ref=totp.encrypt_secret(totp.generate_secret()), disabled_at=timezone.now()
        )

        response = self.client.post(LOGIN_URL, {'email': 'payroll@example.com', 'password': 'correct-password'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('second_factor_enrollment_required'))

    def test_a_code_cannot_be_replayed(self):
        user = _in_group('payroll@example.com', 'Payroll Officer')
        secret = totp.generate_secret()
        SecondFactor.objects.create(user=user, secret_ref=totp.encrypt_secret(secret))
        code = pyotp.TOTP(secret).now()

        first = self.client.post(LOGIN_URL, {
            'email': 'payroll@example.com', 'password': 'correct-password', 'totp_code': code,
        })
        self.client.post('/api/auth/logout/')
        second = self.client.post(LOGIN_URL, {
            'email': 'payroll@example.com', 'password': 'correct-password', 'totp_code': code,
        })

        self.assertEqual(first.status_code, 200)
        self.assertIn('sessionid', first.cookies)
        self.assertEqual(second.status_code, 200)
        self.assertTrue(second.data.get('second_factor_required'))

    def test_ordinary_role_logs_in_without_a_factor(self):
        User.objects.create_user(email='employee@example.com', password='correct-password')

        response = self.client.post(LOGIN_URL, {'email': 'employee@example.com', 'password': 'correct-password'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('sessionid', response.cookies)
