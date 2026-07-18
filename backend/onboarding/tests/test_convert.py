"""`POST /api/onboarding/convert/`, `docs/06-api-contracts.md` §4.7."""
from rest_framework.test import APITestCase

from departments.models import Department, JobTitle
from employees.models import Employee
from iam.roles import HR_ADMINISTRATOR, HR_OFFICER, RECRUITER
from onboarding.models import OnboardingChecklist
from recruitment.models import Candidate, CandidateApplication, JobPosting, JobRequisition, OfferLetter

from .helpers import user_with_role


class ConvertFromApplicationTests(APITestCase):
    def setUp(self):
        self.hr_officer = user_with_role('hro@example.com', HR_OFFICER)
        recruiter = user_with_role('recruiter@example.com', RECRUITER)
        self.department = Department.objects.create(name='Engineering')
        self.job_title = JobTitle.objects.create(name='Engineer')
        requisition = JobRequisition.objects.create(
            department=self.department, job_title=self.job_title, requested_by=recruiter,
            status=JobRequisition.STATUS_APPROVED,
        )
        posting = JobPosting.objects.create(
            requisition=requisition, title='Backend Engineer', description='Build things.',
            channel=JobPosting.CHANNEL_INTERNAL,
        )
        self.candidate = Candidate.objects.create(first_name='Grace', last_name='Hopper', email='grace@example.com')
        self.application = CandidateApplication.objects.create(
            candidate=self.candidate, posting=posting, stage=CandidateApplication.STAGE_OFFER,
        )
        self.payload = {
            'application_id': self.application.pk,
            'employee_number': 'EMP-1001',
            'date_of_birth': '1990-01-01',
            'department': self.department.pk,
            'job_title': self.job_title.pk,
            'hire_date': '2026-08-01',
        }

    def test_hr_officer_can_convert_an_accepted_offer_to_an_employee_and_checklist(self):
        OfferLetter.objects.create(
            application=self.application, offered_salary='95000.00', status=OfferLetter.STATUS_ACCEPTED,
        )
        self.client.force_authenticate(self.hr_officer)

        response = self.client.post('/api/onboarding/convert/', self.payload)

        self.assertEqual(response.status_code, 201)
        checklist = OnboardingChecklist.objects.get(pk=response.data['id'])
        self.assertEqual(checklist.employee.employee_number, 'EMP-1001')
        self.assertEqual(checklist.application, self.application)
        self.application.refresh_from_db()
        self.assertEqual(self.application.stage, CandidateApplication.STAGE_HIRED)

    def test_conversion_rejected_when_no_accepted_offer_exists(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.post('/api/onboarding/convert/', self.payload)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Employee.objects.exists())
        self.assertFalse(OnboardingChecklist.objects.exists())
        self.application.refresh_from_db()
        self.assertEqual(self.application.stage, CandidateApplication.STAGE_OFFER)

    def test_conversion_rejected_when_application_not_at_offer_stage(self):
        self.application.stage = CandidateApplication.STAGE_SCREENING
        self.application.save(update_fields=['stage'])
        self.client.force_authenticate(self.hr_officer)

        response = self.client.post('/api/onboarding/convert/', self.payload)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(OnboardingChecklist.objects.exists())

    def test_recruiter_cannot_convert(self):
        OfferLetter.objects.create(
            application=self.application, offered_salary='95000.00', status=OfferLetter.STATUS_ACCEPTED,
        )
        recruiter = user_with_role('recruiter2@example.com', RECRUITER)
        self.client.force_authenticate(recruiter)

        response = self.client.post('/api/onboarding/convert/', self.payload)

        self.assertEqual(response.status_code, 403)

    def test_hr_administrator_cannot_convert(self):
        OfferLetter.objects.create(
            application=self.application, offered_salary='95000.00', status=OfferLetter.STATUS_ACCEPTED,
        )
        hr_admin = user_with_role('hra@example.com', HR_ADMINISTRATOR)
        self.client.force_authenticate(hr_admin)

        response = self.client.post('/api/onboarding/convert/', self.payload)

        self.assertEqual(response.status_code, 403)


class ConvertDirectHireTests(APITestCase):
    def setUp(self):
        self.hr_officer = user_with_role('hro@example.com', HR_OFFICER)
        self.department = Department.objects.create(name='Engineering')
        self.job_title = JobTitle.objects.create(name='Engineer')

    def test_hr_officer_can_convert_a_direct_hire_with_no_prior_application(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.post('/api/onboarding/convert/', {
            'employee_number': 'EMP-2001',
            'first_name': 'Ada',
            'last_name': 'Lovelace',
            'date_of_birth': '1988-05-05',
            'department': self.department.pk,
            'job_title': self.job_title.pk,
            'hire_date': '2026-08-01',
        })

        self.assertEqual(response.status_code, 201)
        checklist = OnboardingChecklist.objects.get(pk=response.data['id'])
        self.assertIsNone(checklist.application)
        self.assertEqual(checklist.employee.employee_number, 'EMP-2001')
