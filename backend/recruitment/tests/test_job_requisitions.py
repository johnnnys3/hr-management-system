"""`/api/job-requisitions/`, `docs/06-api-contracts.md` §4.6."""
from rest_framework.test import APITestCase

from departments.models import Department, JobTitle
from iam.roles import HR_ADMINISTRATOR, RECRUITER
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
        self.recruiter = user_with_role('recruiter@example.com', RECRUITER)
        self.hr_admin = user_with_role('hradmin@example.com', HR_ADMINISTRATOR)
        self.department = Department.objects.create(name='Engineering')
        self.job_title = JobTitle.objects.create(name='Engineer')

    def test_recruiter_can_create_a_requisition(self):
        self.client.force_authenticate(self.recruiter)

        response = self.client.post(
            REQUISITIONS_URL, {'department': self.department.pk, 'job_title': self.job_title.pk},
        )

        self.assertEqual(response.status_code, 201)
        requisition = JobRequisition.objects.get(pk=response.data['id'])
        self.assertEqual(requisition.status, JobRequisition.STATUS_DRAFT)
        self.assertEqual(requisition.requested_by_id, self.recruiter.pk)

    def test_status_is_not_client_settable_at_creation(self):
        self.client.force_authenticate(self.recruiter)

        response = self.client.post(
            REQUISITIONS_URL,
            {'department': self.department.pk, 'job_title': self.job_title.pk, 'status': JobRequisition.STATUS_APPROVED},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], JobRequisition.STATUS_DRAFT)

    def test_hr_administrator_can_read_but_not_create(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.get(REQUISITIONS_URL)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            REQUISITIONS_URL, {'department': self.department.pk, 'job_title': self.job_title.pk},
        )
        self.assertEqual(response.status_code, 403)

    def test_hr_administrator_can_approve(self):
        requisition = JobRequisition.objects.create(
            department=self.department, job_title=self.job_title, requested_by=self.recruiter,
        )
        self.client.force_authenticate(self.hr_admin)

        response = self.client.post(_approve_url(requisition.pk))

        self.assertEqual(response.status_code, 200)
        requisition.refresh_from_db()
        self.assertEqual(requisition.status, JobRequisition.STATUS_APPROVED)
        self.assertEqual(requisition.approved_by_id, self.hr_admin.pk)

    def test_hr_administrator_can_reject(self):
        requisition = JobRequisition.objects.create(
            department=self.department, job_title=self.job_title, requested_by=self.recruiter,
        )
        self.client.force_authenticate(self.hr_admin)

        response = self.client.post(_reject_url(requisition.pk))

        self.assertEqual(response.status_code, 200)
        requisition.refresh_from_db()
        self.assertEqual(requisition.status, JobRequisition.STATUS_REJECTED)

    def test_recruiter_cannot_approve(self):
        requisition = JobRequisition.objects.create(
            department=self.department, job_title=self.job_title, requested_by=self.recruiter,
        )
        self.client.force_authenticate(self.recruiter)

        response = self.client.post(_approve_url(requisition.pk))

        self.assertEqual(response.status_code, 403)

    def test_recruiter_can_update_own_requisition(self):
        requisition = JobRequisition.objects.create(
            department=self.department, job_title=self.job_title, requested_by=self.recruiter,
        )
        self.client.force_authenticate(self.recruiter)

        other_job_title = JobTitle.objects.create(name='Senior Engineer')
        response = self.client.patch(_detail_url(requisition.pk), {'job_title': other_job_title.pk})

        self.assertEqual(response.status_code, 200)
        requisition.refresh_from_db()
        self.assertEqual(requisition.job_title_id, other_job_title.pk)

    def test_anonymous_is_denied(self):
        response = self.client.get(REQUISITIONS_URL)

        self.assertEqual(response.status_code, 401)
