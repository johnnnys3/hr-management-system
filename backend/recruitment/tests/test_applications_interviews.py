"""`/api/candidates/{id}/applications/` and
`/api/applications/{id}/interviews/`, `docs/06-api-contracts.md` §4.6."""
from datetime import date, timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from departments.models import Department, JobTitle
from employees.models import Employee
from iam.roles import RECRUITER
from recruitment.models import Candidate, CandidateApplication, Interview, JobPosting, JobRequisition

from .helpers import user_with_role


class ApplicationTests(APITestCase):
    def setUp(self):
        self.recruiter = user_with_role('recruiter@example.com', RECRUITER)
        self.candidate = Candidate.objects.create(first_name='Grace', last_name='Hopper', email='grace@example.com')
        department = Department.objects.create(name='Engineering')
        job_title = JobTitle.objects.create(name='Engineer')
        requisition = JobRequisition.objects.create(
            department=department, job_title=job_title, requested_by=self.recruiter,
            status=JobRequisition.STATUS_APPROVED,
        )
        self.posting = JobPosting.objects.create(
            requisition=requisition, title='Backend Engineer', description='Build things.',
            channel=JobPosting.CHANNEL_INTERNAL,
        )

    def test_recruiter_can_create_an_application(self):
        self.client.force_authenticate(self.recruiter)

        response = self.client.post(
            f'/api/candidates/{self.candidate.pk}/applications/', {'posting': self.posting.pk},
        )

        self.assertEqual(response.status_code, 201)
        application = CandidateApplication.objects.get(pk=response.data['id'])
        self.assertEqual(application.candidate_id, self.candidate.pk)
        self.assertEqual(application.stage, CandidateApplication.STAGE_APPLIED)

    def test_anonymous_is_denied(self):
        response = self.client.get(f'/api/candidates/{self.candidate.pk}/applications/')

        self.assertEqual(response.status_code, 401)


class InterviewTests(APITestCase):
    def setUp(self):
        self.recruiter = user_with_role('recruiter@example.com', RECRUITER)
        candidate = Candidate.objects.create(first_name='Grace', last_name='Hopper', email='grace@example.com')
        department = Department.objects.create(name='Engineering')
        job_title = JobTitle.objects.create(name='Engineer')
        requisition = JobRequisition.objects.create(
            department=department, job_title=job_title, requested_by=self.recruiter,
            status=JobRequisition.STATUS_APPROVED,
        )
        posting = JobPosting.objects.create(
            requisition=requisition, title='Backend Engineer', description='Build things.',
            channel=JobPosting.CHANNEL_INTERNAL,
        )
        self.application = CandidateApplication.objects.create(candidate=candidate, posting=posting)
        self.interviewer = Employee.objects.create(
            employee_number='E-1', first_name='Ada', last_name='Lovelace',
            date_of_birth='1990-01-01', department=department, job_title=job_title, hire_date=date.today(),
        )

    def test_recruiter_can_schedule_an_interview(self):
        self.client.force_authenticate(self.recruiter)
        scheduled_at = timezone.now() + timedelta(days=3)

        response = self.client.post(f'/api/applications/{self.application.pk}/interviews/', {
            'interviewer_employee': self.interviewer.pk, 'scheduled_at': scheduled_at.isoformat(),
        })

        self.assertEqual(response.status_code, 201)

    def test_interviewer_need_not_be_a_recruiter(self):
        """HRMS-FR-018 does not restrict who may be scheduled as interviewer,
        only who may schedule/update — `self.interviewer` holds no group at
        all and is still accepted as `interviewer_employee`. Recording the
        outcome (status, feedback) remains Recruiter-only, per
        `IsRecruiter` on this endpoint."""
        self.client.force_authenticate(self.recruiter)
        scheduled_at = timezone.now() + timedelta(days=3)
        response = self.client.post(f'/api/applications/{self.application.pk}/interviews/', {
            'interviewer_employee': self.interviewer.pk, 'scheduled_at': scheduled_at.isoformat(),
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['interviewer_employee'], self.interviewer.pk)

    def test_recruiter_can_record_interview_outcome(self):
        self.client.force_authenticate(self.recruiter)
        scheduled_at = timezone.now() + timedelta(days=3)
        response = self.client.post(f'/api/applications/{self.application.pk}/interviews/', {
            'interviewer_employee': self.interviewer.pk, 'scheduled_at': scheduled_at.isoformat(),
        })
        interview_id = response.data['id']

        response = self.client.patch(
            f'/api/applications/{self.application.pk}/interviews/{interview_id}/',
            {'status': Interview.STATUS_COMPLETED, 'feedback': 'Strong candidate.'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], Interview.STATUS_COMPLETED)

    def test_anonymous_is_denied(self):
        response = self.client.get(f'/api/applications/{self.application.pk}/interviews/')

        self.assertEqual(response.status_code, 401)
