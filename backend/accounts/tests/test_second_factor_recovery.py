"""HRMS-NFR-024: recovery of a lost factor requires approval by a user who
does not administer accounts or credentials. `docs/07-iam-rbac.md` §7.3/§8
defers the approver-holder designation to deployment; this module builds
the mechanism the deployment condition plugs into."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework.test import APITestCase

from accounts.models import SecondFactor, SecondFactorRecoveryRequest

User = get_user_model()

LOGIN_URL = '/api/auth/login/'
RECOVERY_URL = '/api/auth/second-factor/recovery-requests/'


def _decide_url(pk):
    return f'/api/auth/second-factor/recovery-requests/{pk}/decide/'


class CreateRecoveryRequestTests(APITestCase):
    def test_authenticated_user_can_request_their_own_recovery(self):
        user = User.objects.create_user(email='alice@example.com', password='x')
        self.client.force_authenticate(user)

        response = self.client.post(RECOVERY_URL)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(SecondFactorRecoveryRequest.objects.get().user, user)
        self.assertEqual(response.data['status'], 'pending')

    def test_anonymous_cannot_request_recovery(self):
        response = self.client.post(RECOVERY_URL)

        self.assertEqual(response.status_code, 401)

    def test_pending_enrollment_session_cannot_request_recovery(self):
        """A session established for first-time enrolment (`IsFullyAuthenticated`)
        can only reach enrolment and logout — nothing else, including a
        recovery request for a factor that, by definition, isn't enrolled yet."""
        user = User.objects.create_user(email='admin@example.com', password='correct-password')
        group, _ = Group.objects.get_or_create(name='System Administrator')
        user.groups.add(group)
        login_response = self.client.post(LOGIN_URL, {'email': 'admin@example.com', 'password': 'correct-password'})
        assert login_response.data.get('second_factor_enrollment_required')

        response = self.client.post(RECOVERY_URL)

        self.assertEqual(response.status_code, 403)


class DecideRecoveryRequestTests(APITestCase):
    def setUp(self):
        self.requester = User.objects.create_user(email='payroll@example.com', password='x')
        SecondFactor.objects.create(user=self.requester, secret_ref='irrelevant')
        self.recovery_request = SecondFactorRecoveryRequest.objects.create(user=self.requester)

    def _approver_with_permission(self):
        approver = User.objects.create_user(email='approver@example.com', password='x')
        approver.user_permissions.add(
            Permission.objects.get(codename='decide_recovery_request')
        )
        return approver

    def test_holder_of_the_permission_can_approve(self):
        approver = self._approver_with_permission()
        self.client.force_authenticate(approver)

        response = self.client.post(_decide_url(self.recovery_request.pk), {'decision': 'approved'})

        self.assertEqual(response.status_code, 200)
        self.recovery_request.refresh_from_db()
        self.assertEqual(self.recovery_request.status, 'approved')
        self.assertEqual(self.recovery_request.approver, approver)

    def test_approval_disables_the_existing_factor(self):
        approver = self._approver_with_permission()
        self.client.force_authenticate(approver)

        self.client.post(_decide_url(self.recovery_request.pk), {'decision': 'approved'})

        second_factor = SecondFactor.objects.get(user=self.requester)
        self.assertIsNotNone(second_factor.disabled_at)

    def test_denial_leaves_the_factor_enrolled(self):
        approver = self._approver_with_permission()
        self.client.force_authenticate(approver)

        self.client.post(_decide_url(self.recovery_request.pk), {'decision': 'denied'})

        second_factor = SecondFactor.objects.get(user=self.requester)
        self.assertIsNone(second_factor.disabled_at)

    def test_requester_cannot_decide_their_own_request(self):
        """Mirrors the payroll self-approval prohibition (HRMS-BR-008) at the
        identity layer this module can enforce without RBAC/IAM built yet."""
        self.requester.user_permissions.add(Permission.objects.get(codename='decide_recovery_request'))
        self.client.force_authenticate(self.requester)

        response = self.client.post(_decide_url(self.recovery_request.pk), {'decision': 'approved'})

        self.assertEqual(response.status_code, 403)

    def test_user_without_the_permission_is_denied(self):
        bystander = User.objects.create_user(email='bystander@example.com', password='x')
        self.client.force_authenticate(bystander)

        response = self.client.post(_decide_url(self.recovery_request.pk), {'decision': 'approved'})

        self.assertEqual(response.status_code, 403)

    def test_anonymous_is_denied(self):
        response = self.client.post(_decide_url(self.recovery_request.pk), {'decision': 'approved'})

        self.assertEqual(response.status_code, 401)

    def test_an_already_decided_request_cannot_be_decided_again(self):
        approver = self._approver_with_permission()
        self.client.force_authenticate(approver)
        self.client.post(_decide_url(self.recovery_request.pk), {'decision': 'denied'})

        response = self.client.post(_decide_url(self.recovery_request.pk), {'decision': 'approved'})

        self.assertEqual(response.status_code, 409)
        self.recovery_request.refresh_from_db()
        self.assertEqual(self.recovery_request.status, 'denied')
