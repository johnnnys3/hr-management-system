"""`/api/job-titles/`, `docs/06-api-contracts.md` §4.4: same permission
shape as `/api/departments/`, `docs/07-iam-rbac.md` §4.2's HR
configuration row."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

from departments.models import JobTitle
from iam.roles import HR_ADMINISTRATOR, HR_OFFICER

User = get_user_model()

JOB_TITLES_URL = '/api/job-titles/'


def _detail_url(pk):
    return f'/api/job-titles/{pk}/'


def _user_with_role(email, role_name):
    user = User.objects.create_user(email=email, password='x')
    user.groups.add(Group.objects.get(name=role_name))
    return user


class JobTitleListCreateTests(APITestCase):
    def setUp(self):
        self.hr_admin = _user_with_role('hradmin@example.com', HR_ADMINISTRATOR)
        self.hr_officer = _user_with_role('hrofficer@example.com', HR_OFFICER)

    def test_hr_administrator_can_create_a_job_title(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.post(JOB_TITLES_URL, {'name': 'Software Engineer'})

        self.assertEqual(response.status_code, 201)
        self.assertTrue(JobTitle.objects.filter(name='Software Engineer').exists())

    def test_hr_officer_cannot_create_a_job_title(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.post(JOB_TITLES_URL, {'name': 'Software Engineer'})

        self.assertEqual(response.status_code, 403)

    def test_hr_officer_can_read_job_titles(self):
        JobTitle.objects.create(name='Software Engineer')
        self.client.force_authenticate(self.hr_officer)

        response = self.client.get(JOB_TITLES_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_anonymous_is_denied(self):
        response = self.client.get(JOB_TITLES_URL)

        self.assertEqual(response.status_code, 401)


class JobTitleDetailTests(APITestCase):
    def setUp(self):
        self.hr_admin = _user_with_role('hradmin@example.com', HR_ADMINISTRATOR)
        self.hr_officer = _user_with_role('hrofficer@example.com', HR_OFFICER)
        self.job_title = JobTitle.objects.create(name='Software Engineer')

    def test_hr_administrator_can_retire_a_job_title(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.patch(_detail_url(self.job_title.pk), {'is_active': False})

        self.assertEqual(response.status_code, 200)
        self.job_title.refresh_from_db()
        self.assertFalse(self.job_title.is_active)

    def test_hr_officer_cannot_update_a_job_title(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.patch(_detail_url(self.job_title.pk), {'is_active': False})

        self.assertEqual(response.status_code, 403)
