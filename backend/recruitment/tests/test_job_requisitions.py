"""`/api/job-requisitions/`, `docs/06-api-contracts.md` §4.6."""
from rest_framework.test import APITestCase

from departments.models import Department, JobTitle
from iam.roles import HR_ADMINISTRATOR, HR_OFFICER
from notifications.models import Notification
from recruitment.models import JobRequisition

from .helpers import user_with_role

REQUISITIONS_URL = '/api/job-requisitions/'


def _detail_url(pk):
    return f'/api/job-requisitions/{pk}/'


def _approve_url(pk):
    return f'/api/job-requisitions/{pk}/approve/'


def _reject_url(pk):
    return f'/api/job-requisitions/{pk}/reject/'


class JobRequisitionTests(APITestCase):
    def setUp(self):
        # ADR-0013: Recruiter is retired, merged into HR Administrator.
        # Two distinct HR Administrator accounts stand in for the old
        # Recruiter/HR Administrator pair, so creation and approval are
        # still exercised by different users.
        self.hr_admin = user_with_role('hradmin@example.com', HR_ADMINISTRATOR)
        self.hr_admin_2 = user_with_role('hradmin2@example.com', HR_ADMINISTRATOR)
        self.hr_officer = user_with_role('hrofficer@example.com', HR_OFFICER)
        self.department = Department.objects.create(name='Engineering')
        self.job_title = JobTitle.objects.create(name='Engineer')

    def test_hr_administrator_can_create_a_requisition(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.post(
            REQUISITIONS_URL, {'department': self.department.pk, 'job_title': self.job_title.pk},
        )

        self.assertEqual(response.status_code, 201)
        requisition = JobRequisition.objects.get(pk=response.data['id'])
        self.assertEqual(requisition.status, JobRequisition.STATUS_DRAFT)
        self.assertEqual(requisition.requested_by_id, self.hr_admin.pk)

    def test_status_is_not_client_settable_at_creation(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.post(
            REQUISITIONS_URL,
            {'department': self.department.pk, 'job_title': self.job_title.pk, 'status': JobRequisition.STATUS_APPROVED},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], JobRequisition.STATUS_DRAFT)

    def test_hr_officer_cannot_read_or_create(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.get(REQUISITIONS_URL)
        self.assertEqual(response.status_code, 403)

        response = self.client.post(
            REQUISITIONS_URL, {'department': self.department.pk, 'job_title': self.job_title.pk},
        )
        self.assertEqual(response.status_code, 403)

    def test_a_different_hr_administrator_can_approve(self):
        requisition = JobRequisition.objects.create(
            department=self.department, job_title=self.job_title, requested_by=self.hr_admin,
        )
        self.client.force_authenticate(self.hr_admin_2)

        response = self.client.post(_approve_url(requisition.pk))

        self.assertEqual(response.status_code, 200)
        requisition.refresh_from_db()
        self.assertEqual(requisition.status, JobRequisition.STATUS_APPROVED)
        self.assertEqual(requisition.approved_by_id, self.hr_admin_2.pk)
        notification = Notification.objects.get(related_type='job_requisition', related_id=requisition.pk)
        self.assertEqual(notification.recipient_id, self.hr_admin.pk)
        self.assertEqual(notification.category, Notification.CATEGORY_REQUEST_UPDATE)

    def test_a_different_hr_administrator_can_reject(self):
        requisition = JobRequisition.objects.create(
            department=self.department, job_title=self.job_title, requested_by=self.hr_admin,
        )
        self.client.force_authenticate(self.hr_admin_2)

        response = self.client.post(_reject_url(requisition.pk))

        self.assertEqual(response.status_code, 200)
        requisition.refresh_from_db()
        self.assertEqual(requisition.status, JobRequisition.STATUS_REJECTED)
        notification = Notification.objects.get(related_type='job_requisition', related_id=requisition.pk)
        self.assertEqual(notification.recipient_id, self.hr_admin.pk)
        self.assertEqual(notification.category, Notification.CATEGORY_REQUEST_UPDATE)

    def test_requester_cannot_approve_own_requisition(self):
        """ADR-0013: HR Administrator now both creates and approves
        requisitions, so self-approval must be rejected explicitly —
        mirrors `PayrollRunApproveView`'s `self_approval_forbidden`."""
        requisition = JobRequisition.objects.create(
            department=self.department, job_title=self.job_title, requested_by=self.hr_admin,
        )
        self.client.force_authenticate(self.hr_admin)

        response = self.client.post(_approve_url(requisition.pk))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['code'], 'self_approval_forbidden')
        requisition.refresh_from_db()
        self.assertEqual(requisition.status, JobRequisition.STATUS_DRAFT)

    def test_hr_administrator_can_update_a_requisition(self):
        requisition = JobRequisition.objects.create(
            department=self.department, job_title=self.job_title, requested_by=self.hr_admin,
        )
        self.client.force_authenticate(self.hr_admin)

        other_job_title = JobTitle.objects.create(name='Senior Engineer')
        response = self.client.patch(_detail_url(requisition.pk), {'job_title': other_job_title.pk})

        self.assertEqual(response.status_code, 200)
        requisition.refresh_from_db()
        self.assertEqual(requisition.job_title_id, other_job_title.pk)

    def test_anonymous_is_denied(self):
        response = self.client.get(REQUISITIONS_URL)

        self.assertEqual(response.status_code, 401)

    def test_an_already_approved_requisition_cannot_be_approved_again(self):
        requisition = JobRequisition.objects.create(
            department=self.department, job_title=self.job_title, requested_by=self.hr_admin,
            status=JobRequisition.STATUS_APPROVED, approved_by=self.hr_admin_2,
        )
        self.client.force_authenticate(self.hr_admin_2)

        response = self.client.post(_approve_url(requisition.pk))

        self.assertEqual(response.status_code, 400)

    def test_a_rejected_requisition_cannot_be_approved(self):
        requisition = JobRequisition.objects.create(
            department=self.department, job_title=self.job_title, requested_by=self.hr_admin,
            status=JobRequisition.STATUS_REJECTED,
        )
        self.client.force_authenticate(self.hr_admin_2)

        response = self.client.post(_approve_url(requisition.pk))

        self.assertEqual(response.status_code, 400)
