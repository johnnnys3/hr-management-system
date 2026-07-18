"""`/api/candidates/`, `docs/06-api-contracts.md` §4.6."""
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from iam.roles import HR_ADMINISTRATOR, RECRUITER
from recruitment.models import Candidate

from .helpers import user_with_role

CANDIDATES_URL = '/api/candidates/'

_PDF_BYTES = b'%PDF-1.4 fake pdf content'


def _detail_url(pk):
    return f'/api/candidates/{pk}/'


class CandidateTests(APITestCase):
    def setUp(self):
        self.recruiter = user_with_role('recruiter@example.com', RECRUITER)
        self.hr_admin = user_with_role('hradmin@example.com', HR_ADMINISTRATOR)

    def test_recruiter_can_create_a_candidate_without_a_resume(self):
        self.client.force_authenticate(self.recruiter)

        response = self.client.post(CANDIDATES_URL, {
            'first_name': 'Grace', 'last_name': 'Hopper', 'email': 'grace@example.com',
        })

        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.data['resume_object_key'])

    def test_recruiter_can_create_a_candidate_with_a_resume(self):
        self.client.force_authenticate(self.recruiter)
        resume = SimpleUploadedFile('resume.pdf', _PDF_BYTES, content_type='application/pdf')

        response = self.client.post(CANDIDATES_URL, {
            'first_name': 'Ada', 'last_name': 'Lovelace', 'email': 'ada@example.com', 'resume': resume,
        }, format='multipart')

        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.data['resume_object_key'])
        candidate = Candidate.objects.get(pk=response.data['id'])
        self.assertTrue(candidate.resume_object_key.startswith(f'candidate-resumes/{candidate.pk}/'))

    def test_unrecognised_resume_file_type_is_rejected(self):
        self.client.force_authenticate(self.recruiter)
        resume = SimpleUploadedFile('resume.exe', b'not a real document', content_type='application/octet-stream')

        response = self.client.post(CANDIDATES_URL, {
            'first_name': 'Ada', 'last_name': 'Lovelace', 'email': 'ada@example.com', 'resume': resume,
        }, format='multipart')

        self.assertEqual(response.status_code, 400)

    def test_email_is_not_unique_across_applications(self):
        self.client.force_authenticate(self.recruiter)
        Candidate.objects.create(first_name='Ada', last_name='Lovelace', email='ada@example.com')

        response = self.client.post(CANDIDATES_URL, {
            'first_name': 'Ada', 'last_name': 'Lovelace', 'email': 'ada@example.com',
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Candidate.objects.filter(email='ada@example.com').count(), 2)

    def test_hr_administrator_cannot_access_candidates(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.get(CANDIDATES_URL)

        self.assertEqual(response.status_code, 403)

    def test_anonymous_is_denied(self):
        response = self.client.get(CANDIDATES_URL)

        self.assertEqual(response.status_code, 401)
