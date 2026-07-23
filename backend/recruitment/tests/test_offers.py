"""`/api/applications/{id}/offer/` and `/api/offers/{id}/decide/`,
`docs/06-api-contracts.md` §4.6."""
from rest_framework.test import APITestCase

from departments.models import Department, JobTitle
from iam.roles import HR_OFFICER, RECRUITER
from recruitment.models import Candidate, CandidateApplication, JobPosting, JobRequisition, OfferLetter

from .helpers import user_with_role


class OfferLetterTests(APITestCase):
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

    def test_recruiter_can_issue_an_offer_and_a_document_is_generated(self):
        self.client.force_authenticate(self.recruiter)

        response = self.client.post(
            f'/api/applications/{self.application.pk}/offer/', {'offered_salary': '95000.00'},
        )

        self.assertEqual(response.status_code, 201)
        offer = OfferLetter.objects.get(pk=response.data['id'])
        self.assertEqual(offer.status, OfferLetter.STATUS_PENDING)
        self.assertIsNotNone(offer.document_object_key)
        self.assertTrue(offer.document_object_key.startswith(f'offer-letters/{offer.pk}/'))

    def test_issuing_an_offer_advances_the_application_to_offer_stage(self):
        """Nothing else in this app ever writes `stage` — found via the E2E
        suite, since onboarding's convert endpoint (HRMS-BR-013) requires
        `stage == 'offer'` but no endpoint set it, making conversion
        permanently unreachable for any real application."""
        self.assertEqual(self.application.stage, CandidateApplication.STAGE_APPLIED)
        self.client.force_authenticate(self.recruiter)

        self.client.post(f'/api/applications/{self.application.pk}/offer/', {'offered_salary': '95000.00'})

        self.application.refresh_from_db()
        self.assertEqual(self.application.stage, CandidateApplication.STAGE_OFFER)

    def test_issuing_a_second_offer_does_not_error_on_an_already_advanced_stage(self):
        self.client.force_authenticate(self.recruiter)
        self.client.post(f'/api/applications/{self.application.pk}/offer/', {'offered_salary': '95000.00'})

        response = self.client.post(f'/api/applications/{self.application.pk}/offer/', {'offered_salary': '100000.00'})

        self.assertEqual(response.status_code, 201)
        self.application.refresh_from_db()
        self.assertEqual(self.application.stage, CandidateApplication.STAGE_OFFER)

    def test_negative_salary_is_rejected(self):
        self.client.force_authenticate(self.recruiter)

        response = self.client.post(
            f'/api/applications/{self.application.pk}/offer/', {'offered_salary': '-1.00'},
        )

        self.assertEqual(response.status_code, 400)

    def test_recruiter_can_record_a_decision(self):
        self.client.force_authenticate(self.recruiter)
        create_response = self.client.post(
            f'/api/applications/{self.application.pk}/offer/', {'offered_salary': '95000.00'},
        )

        response = self.client.post(
            f'/api/offers/{create_response.data["id"]}/decide/', {'decision': OfferLetter.STATUS_ACCEPTED},
        )

        self.assertEqual(response.status_code, 200)
        offer = OfferLetter.objects.get(pk=create_response.data['id'])
        self.assertEqual(offer.status, OfferLetter.STATUS_ACCEPTED)
        self.assertIsNotNone(offer.decided_at)

    def test_acceptance_does_not_itself_create_an_employee(self):
        """HRMS-BR-013: onboarding initiation is the conversion trigger, not
        this endpoint (Module 10, not built by this module)."""
        from employees.models import Employee

        self.client.force_authenticate(self.recruiter)
        create_response = self.client.post(
            f'/api/applications/{self.application.pk}/offer/', {'offered_salary': '95000.00'},
        )
        before_count = Employee.objects.count()

        self.client.post(f'/api/offers/{create_response.data["id"]}/decide/', {'decision': OfferLetter.STATUS_ACCEPTED})

        self.assertEqual(Employee.objects.count(), before_count)

    def test_a_decided_offer_cannot_be_decided_again(self):
        self.client.force_authenticate(self.recruiter)
        create_response = self.client.post(
            f'/api/applications/{self.application.pk}/offer/', {'offered_salary': '95000.00'},
        )
        self.client.post(f'/api/offers/{create_response.data["id"]}/decide/', {'decision': OfferLetter.STATUS_ACCEPTED})

        response = self.client.post(
            f'/api/offers/{create_response.data["id"]}/decide/', {'decision': OfferLetter.STATUS_WITHDRAWN},
        )

        self.assertEqual(response.status_code, 400)

    def test_hr_officer_can_read_but_not_issue_or_decide_offers(self):
        """HR Officer needs read access to reach an accepted offer and trigger
        HRMS-BR-013 conversion (module 9), but has no write access here —
        `docs/07-iam-rbac.md` §4.2 grants Recruiter, not HR Officer, C/U."""
        self.client.force_authenticate(self.recruiter)
        create_response = self.client.post(
            f'/api/applications/{self.application.pk}/offer/', {'offered_salary': '95000.00'},
        )
        offer_id = create_response.data['id']

        hr_officer = user_with_role('hrofficer@example.com', HR_OFFICER)
        self.client.force_authenticate(hr_officer)
        read_response = self.client.get(f'/api/applications/{self.application.pk}/offer/')
        issue_response = self.client.post(
            f'/api/applications/{self.application.pk}/offer/', {'offered_salary': '50000.00'},
        )
        decide_response = self.client.post(
            f'/api/offers/{offer_id}/decide/', {'decision': OfferLetter.STATUS_ACCEPTED},
        )

        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(issue_response.status_code, 403)
        self.assertEqual(decide_response.status_code, 403)

    def test_anonymous_is_denied(self):
        response = self.client.get(f'/api/applications/{self.application.pk}/offer/')

        self.assertEqual(response.status_code, 401)
