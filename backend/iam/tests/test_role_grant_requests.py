"""`docs/07-iam-rbac.md` §7.3: self-grant refused, privileged grant needs
an approver who is not the requester; a non-privileged (Recruiter) grant
takes effect immediately."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import IntegrityError, transaction
from rest_framework.test import APITestCase

from iam.models import RoleGrantRequest
from iam.roles import HR_ADMINISTRATOR, PAYROLL_OFFICER, RECRUITER, SYSTEM_ADMINISTRATOR


User = get_user_model()

REQUESTS_URL = '/api/role-grant-requests/'


def _decide_url(pk):
    return f'/api/role-grant-requests/{pk}/decide/'


class CreateRoleGrantRequestTests(APITestCase):
    def setUp(self):
        self.requester = User.objects.create_user(email='admin@example.com', password='x')
        self.requester.groups.add(Group.objects.get(name=SYSTEM_ADMINISTRATOR))
        self.subject = User.objects.create_user(email='subject@example.com', password='x')
        self.payroll_officer = Group.objects.get(name=PAYROLL_OFFICER)
        self.recruiter = Group.objects.get(name=RECRUITER)

    def test_an_unrelated_group_cannot_be_requested(self):
        """`role_id` is restricted to the six assigned-role groups
        (`docs/07-iam-rbac.md` §2.3) — an arbitrary Django group unrelated
        to RBAC must not be requestable, let alone auto-granted."""
        unrelated_group = Group.objects.create(name='Some Other App Group')
        self.client.force_authenticate(self.requester)

        response = self.client.post(REQUESTS_URL, {
            'subject_user_id': self.subject.pk, 'role_id': unrelated_group.pk,
        })

        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.subject.groups.filter(name='Some Other App Group').exists())

    def test_system_administrator_can_request_a_grant_for_another_user(self):
        self.client.force_authenticate(self.requester)

        response = self.client.post(REQUESTS_URL, {
            'subject_user_id': self.subject.pk, 'role_id': self.payroll_officer.pk,
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'pending')

    def test_non_system_administrator_cannot_request_a_grant(self):
        non_admin = User.objects.create_user(email='not-admin@example.com', password='x')
        self.client.force_authenticate(non_admin)

        response = self.client.post(REQUESTS_URL, {
            'subject_user_id': self.subject.pk, 'role_id': self.payroll_officer.pk,
        })

        self.assertEqual(response.status_code, 403)
        self.assertFalse(RoleGrantRequest.objects.exists())

    def test_self_grant_is_refused_at_the_api_layer(self):
        self.client.force_authenticate(self.requester)

        response = self.client.post(REQUESTS_URL, {
            'subject_user_id': self.requester.pk, 'role_id': self.payroll_officer.pk,
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error']['code'], 'self_grant_forbidden')
        self.assertFalse(RoleGrantRequest.objects.exists())

    def test_self_grant_is_refused_at_the_database_layer(self):
        """Defence in depth: the `CHECK` constraint, not just the view,
        is what `docs/06-api-contracts.md` §4.9 cites as the enforcement."""
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                RoleGrantRequest.objects.create(
                    requester=self.requester, subject=self.requester, role=self.payroll_officer,
                )

    def test_anonymous_cannot_request_a_grant(self):
        response = self.client.post(REQUESTS_URL, {
            'subject_user_id': self.subject.pk, 'role_id': self.payroll_officer.pk,
        })

        self.assertEqual(response.status_code, 401)

    def test_non_privileged_role_grant_takes_effect_immediately(self):
        self.client.force_authenticate(self.requester)

        response = self.client.post(REQUESTS_URL, {
            'subject_user_id': self.subject.pk, 'role_id': self.recruiter.pk,
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'approved')
        self.assertTrue(self.subject.groups.filter(name=RECRUITER).exists())

    def test_privileged_role_grant_does_not_take_effect_until_approved(self):
        self.client.force_authenticate(self.requester)

        response = self.client.post(REQUESTS_URL, {
            'subject_user_id': self.subject.pk, 'role_id': self.payroll_officer.pk,
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'pending')
        self.assertFalse(self.subject.groups.filter(name=PAYROLL_OFFICER).exists())


class ListRoleGrantRequestTests(APITestCase):
    def setUp(self):
        self.requester = User.objects.create_user(email='requester2@example.com', password='x')
        self.subject = User.objects.create_user(email='subject2@example.com', password='x')
        self.payroll_officer = Group.objects.get(name=PAYROLL_OFFICER)
        self.grant_request = RoleGrantRequest.objects.create(
            requester=self.requester, subject=self.subject, role=self.payroll_officer,
        )

    def test_requester_sees_their_own_request(self):
        self.client.force_authenticate(self.requester)

        response = self.client.get(REQUESTS_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual([r['id'] for r in response.data], [self.grant_request.pk])

    def test_eligible_approver_sees_the_pending_request(self):
        approver = User.objects.create_user(email='approver2@example.com', password='x')
        approver.user_permissions.add(Permission.objects.get(codename='approve_role_grant'))
        self.client.force_authenticate(approver)

        response = self.client.get(REQUESTS_URL)

        self.assertEqual([r['id'] for r in response.data], [self.grant_request.pk])

    def test_decided_requests_are_not_shown_to_other_approvers(self):
        self.grant_request.status = RoleGrantRequest.STATUS_APPROVED
        self.grant_request.save(update_fields=['status'])
        approver = User.objects.create_user(email='approver3@example.com', password='x')
        approver.user_permissions.add(Permission.objects.get(codename='approve_role_grant'))
        self.client.force_authenticate(approver)

        response = self.client.get(REQUESTS_URL)

        self.assertEqual(response.data, [])

    def test_bystander_sees_nothing(self):
        bystander = User.objects.create_user(email='bystander2@example.com', password='x')
        self.client.force_authenticate(bystander)

        response = self.client.get(REQUESTS_URL)

        self.assertEqual(response.data, [])

    def test_anonymous_is_denied(self):
        response = self.client.get(REQUESTS_URL)

        self.assertEqual(response.status_code, 401)


class DecideRoleGrantRequestTests(APITestCase):
    def setUp(self):
        self.requester = User.objects.create_user(email='requester@example.com', password='x')
        self.subject = User.objects.create_user(email='subject@example.com', password='x')
        self.payroll_officer = Group.objects.get(name=PAYROLL_OFFICER)
        self.grant_request = RoleGrantRequest.objects.create(
            requester=self.requester, subject=self.subject, role=self.payroll_officer,
        )

    def _approver_with_permission(self):
        approver = User.objects.create_user(email='approver@example.com', password='x')
        approver.user_permissions.add(Permission.objects.get(codename='approve_role_grant'))
        return approver

    def test_holder_of_the_permission_can_approve(self):
        approver = self._approver_with_permission()
        self.client.force_authenticate(approver)

        response = self.client.post(_decide_url(self.grant_request.pk), {'decision': 'approved'})

        self.assertEqual(response.status_code, 200)
        self.grant_request.refresh_from_db()
        self.assertEqual(self.grant_request.status, 'approved')
        self.assertEqual(self.grant_request.approver, approver)

    def test_approval_grants_the_group_membership(self):
        approver = self._approver_with_permission()
        self.client.force_authenticate(approver)

        self.client.post(_decide_url(self.grant_request.pk), {'decision': 'approved'})

        self.assertTrue(self.subject.groups.filter(name=PAYROLL_OFFICER).exists())

    def test_refusal_does_not_grant_the_group_membership(self):
        approver = self._approver_with_permission()
        self.client.force_authenticate(approver)

        response = self.client.post(_decide_url(self.grant_request.pk), {'decision': 'refused'})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.subject.groups.filter(name=PAYROLL_OFFICER).exists())

    def test_requester_cannot_decide_their_own_request(self):
        self.requester.user_permissions.add(Permission.objects.get(codename='approve_role_grant'))
        self.client.force_authenticate(self.requester)

        response = self.client.post(_decide_url(self.grant_request.pk), {'decision': 'approved'})

        self.assertEqual(response.status_code, 403)

    def test_approver_cannot_equal_requester_at_the_database_layer(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.grant_request.approver = self.requester
                self.grant_request.save(update_fields=['approver'])

    def test_user_without_the_permission_is_denied(self):
        bystander = User.objects.create_user(email='bystander@example.com', password='x')
        self.client.force_authenticate(bystander)

        response = self.client.post(_decide_url(self.grant_request.pk), {'decision': 'approved'})

        self.assertEqual(response.status_code, 403)

    def test_anonymous_is_denied(self):
        response = self.client.post(_decide_url(self.grant_request.pk), {'decision': 'approved'})

        self.assertEqual(response.status_code, 401)

    def test_an_already_decided_request_cannot_be_decided_again(self):
        approver = self._approver_with_permission()
        self.client.force_authenticate(approver)
        self.client.post(_decide_url(self.grant_request.pk), {'decision': 'refused'})

        response = self.client.post(_decide_url(self.grant_request.pk), {'decision': 'approved'})

        self.assertEqual(response.status_code, 409)
        self.grant_request.refresh_from_db()
        self.assertEqual(self.grant_request.status, 'refused')

    def test_break_glass_superuser_cannot_decide_a_grant_request(self):
        """§7.2: `is_superuser` is reserved for break-glass, and
        `has_perm` returns `True` for it unconditionally. Without an
        explicit check, that would make the break-glass account an
        unconditional approver of every privileged grant."""
        break_glass = User.objects.create_superuser(email='breakglass@example.com', password='x')
        self.client.force_authenticate(break_glass)

        response = self.client.post(_decide_url(self.grant_request.pk), {'decision': 'approved'})

        self.assertEqual(response.status_code, 403)
        self.grant_request.refresh_from_db()
        self.assertEqual(self.grant_request.status, RoleGrantRequest.STATUS_PENDING)
        self.assertIsNone(self.grant_request.approver)
        self.assertFalse(self.subject.groups.filter(name=PAYROLL_OFFICER).exists())

    def test_approve_role_grant_is_not_granted_to_system_administrator_by_default(self):
        """`docs/07-iam-rbac.md` §7.3/§8: granting this to System
        Administrator by default would reduce the control to detection."""
        admin_group = Group.objects.get(name=SYSTEM_ADMINISTRATOR)
        permission = Permission.objects.get(codename='approve_role_grant')

        self.assertNotIn(permission, admin_group.permissions.all())

    def test_hr_administrator_is_granted_approve_role_grant_by_default(self):
        """`docs/07-iam-rbac.md` §7.3/§8 (amended 2026-07-27): the
        deployment-configured approver defaults to HR Administrator, which
        already satisfies HRMS-NFR-024's scope requirement for the role and
        is not System Administrator — the migration in this task closes
        what was previously an open deployment question."""
        hr_admin_group = Group.objects.get(name=HR_ADMINISTRATOR)
        permission = Permission.objects.get(codename='approve_role_grant')

        self.assertIn(permission, hr_admin_group.permissions.all())
