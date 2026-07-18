"""`/api/job-postings/`, `docs/06-api-contracts.md` §4.6."""
from django.utils import timezone
from rest_framework.test import APITestCase

from departments.models import Department, JobTitle
from iam.roles import HR_ADMINISTRATOR, RECRUITER
from recruitment.models import JobPosting, JobRequisition

from .helpers import user_with_role

POSTINGS_URL = '/api/job-postings/'


def _detail_url(pk):
    return f'/api/job-postings/{pk}/'


def _publish_url(pk):
    return f'/api/job-postings/{pk}/publish/'


class JobPostingTests(APITestCase):
    def setUp(self):
        self.recruiter = user_with_role('recruiter@example.com', RECRUITER)
        self.hr_admin = user_with_role('hradmin@example.com', HR_ADMINISTRATOR)
        department = Department.objects.create(name='Engineering')
        job_title = JobTitle.objects.create(name='Engineer')
        self.approved_requisition = JobRequisition.objects.create(
            department=department, job_title=job_title, requested_by=self.recruiter,
            status=JobRequisition.STATUS_APPROVED, approved_by=self.hr_admin,
        )
        self.draft_requisition = JobRequisition.objects.create(
            department=department, job_title=job_title, requested_by=self.recruiter,
        )

    def test_recruiter_can_create_a_posting_for_an_approved_requisition(self):
        self.client.force_authenticate(self.recruiter)

        response = self.client.post(POSTINGS_URL, {
            'requisition': self.approved_requisition.pk,
            'title': 'Backend Engineer',
            'description': 'Build things.',
            'channel': JobPosting.CHANNEL_INTERNAL,
        })

        self.assertEqual(response.status_code, 201)

    def test_posting_rejected_for_unapproved_requisition(self):
        self.client.force_authenticate(self.recruiter)

        response = self.client.post(POSTINGS_URL, {
            'requisition': self.draft_requisition.pk,
            'title': 'Backend Engineer',
            'description': 'Build things.',
            'channel': JobPosting.CHANNEL_INTERNAL,
        })

        self.assertEqual(response.status_code, 400)

    def test_external_channel_is_accepted_without_a_job_board_integration(self):
        """`docs/02-project-plan.md` §8 TBD-012: the `channel` value exists
        regardless of whether the external integration itself is built."""
        self.client.force_authenticate(self.recruiter)

        response = self.client.post(POSTINGS_URL, {
            'requisition': self.approved_requisition.pk,
            'title': 'Backend Engineer',
            'description': 'Build things.',
            'channel': JobPosting.CHANNEL_EXTERNAL,
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['channel'], JobPosting.CHANNEL_EXTERNAL)

    def test_recruiter_can_publish(self):
        posting = JobPosting.objects.create(
            requisition=self.approved_requisition, title='Backend Engineer', description='Build things.',
            channel=JobPosting.CHANNEL_INTERNAL,
        )
        self.client.force_authenticate(self.recruiter)

        response = self.client.post(_publish_url(posting.pk))

        self.assertEqual(response.status_code, 200)
        posting.refresh_from_db()
        self.assertIsNotNone(posting.published_at)
        self.assertLessEqual(posting.published_at, timezone.now())

    def test_publishing_an_already_published_posting_is_rejected(self):
        posting = JobPosting.objects.create(
            requisition=self.approved_requisition, title='Backend Engineer', description='Build things.',
            channel=JobPosting.CHANNEL_INTERNAL, published_at=timezone.now(),
        )
        self.client.force_authenticate(self.recruiter)

        response = self.client.post(_publish_url(posting.pk))

        self.assertEqual(response.status_code, 400)

    def test_patch_cannot_reassign_a_posting_to_an_unapproved_requisition(self):
        posting = JobPosting.objects.create(
            requisition=self.approved_requisition, title='Backend Engineer', description='Build things.',
            channel=JobPosting.CHANNEL_INTERNAL,
        )
        self.client.force_authenticate(self.recruiter)

        response = self.client.patch(_detail_url(posting.pk), {'requisition': self.draft_requisition.pk})

        self.assertEqual(response.status_code, 400)
        posting.refresh_from_db()
        self.assertEqual(posting.requisition_id, self.approved_requisition.pk)

    def test_hr_administrator_cannot_access_postings(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.get(POSTINGS_URL)

        self.assertEqual(response.status_code, 403)

    def test_anonymous_is_denied(self):
        response = self.client.get(POSTINGS_URL)

        self.assertEqual(response.status_code, 401)
