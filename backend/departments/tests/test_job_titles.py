"""`/api/job-titles/`, `docs/06-api-contracts.md` §4.4: same permission
shape as `/api/departments/`, `docs/07-iam-rbac.md` §4.2's HR
configuration row."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

from audit.models import AuditLog
from departments.models import JobTitle
from iam.roles import HR_ADMINISTRATOR, HR_OFFICER, PAYROLL_OFFICER, RECRUITER

User = get_user_model()

JOB_TITLES_URL = '/api/job-titles/'


def _detail_url(pk):
    """
    Build the detail endpoint URL for a job title.
    
    Parameters:
    	pk: The primary key of the job title.
    
    Returns:
    	str: The URL for the job title detail endpoint.
    """
    return f'/api/job-titles/{pk}/'


def _user_with_role(email, role_name):
    """
    Create a user with the specified email address and IAM role.
    
    Parameters:
    	email (str): Email address for the new user.
    	role_name (str): Name of the Django group assigned to the user.
    
    Returns:
    	User: The created user.
    """
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

    def test_anonymous_cannot_create(self):
        response = self.client.post(JOB_TITLES_URL, {'name': 'Software Engineer'})

        self.assertEqual(response.status_code, 401)
        self.assertFalse(JobTitle.objects.filter(name='Software Engineer').exists())

    def test_authenticated_user_with_no_group_is_denied(self):
        JobTitle.objects.create(name='Software Engineer')
        bystander = User.objects.create_user(email='bystander@example.com', password='x')
        self.client.force_authenticate(bystander)

        response = self.client.get(JOB_TITLES_URL)

        self.assertEqual(response.status_code, 403)

    def test_break_glass_is_superuser_account_without_role_is_denied(self):
        break_glass = User.objects.create_superuser(email='breakglass@example.com', password='x')
        self.client.force_authenticate(break_glass)

        response = self.client.post(JOB_TITLES_URL, {'name': 'Software Engineer'})

        self.assertEqual(response.status_code, 403)

    def test_recruiter_and_payroll_officer_can_read_job_titles(self):
        JobTitle.objects.create(name='Software Engineer')

        for role in (RECRUITER, PAYROLL_OFFICER):
            user = _user_with_role(f'{role.lower().replace(" ", "")}@example.com', role)
            self.client.force_authenticate(user)

            response = self.client.get(JOB_TITLES_URL)

            self.assertEqual(response.status_code, 200)

    def test_job_titles_are_returned_ordered_by_name(self):
        JobTitle.objects.create(name='Software Engineer')
        JobTitle.objects.create(name='Accountant')
        JobTitle.objects.create(name='Recruiter')
        self.client.force_authenticate(self.hr_admin)

        response = self.client.get(JOB_TITLES_URL)

        self.assertEqual(
            [row['name'] for row in response.data],
            ['Accountant', 'Recruiter', 'Software Engineer'],
        )

    def test_duplicate_name_is_rejected(self):
        JobTitle.objects.create(name='Software Engineer')
        self.client.force_authenticate(self.hr_admin)

        response = self.client.post(JOB_TITLES_URL, {'name': 'Software Engineer'})

        self.assertEqual(response.status_code, 400)

    def test_blank_name_is_rejected(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.post(JOB_TITLES_URL, {'name': ''})

        self.assertEqual(response.status_code, 400)

    def test_missing_name_is_rejected(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.post(JOB_TITLES_URL, {})

        self.assertEqual(response.status_code, 400)

    def test_read_only_fields_are_ignored_on_create(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.post(
            JOB_TITLES_URL,
            {'name': 'Software Engineer', 'id': 999, 'created_at': '2000-01-01T00:00:00Z'},
        )

        self.assertEqual(response.status_code, 201)
        job_title = JobTitle.objects.get(name='Software Engineer')
        self.assertNotEqual(job_title.pk, 999)
        self.assertNotEqual(job_title.created_at.year, 2000)

    def test_creating_a_job_title_records_an_audit_log_entry(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.post(JOB_TITLES_URL, {'name': 'Software Engineer'})

        job_title_id = response.data['id']
        self.assertTrue(
            AuditLog.objects.filter(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='job_title_created',
                actor=self.hr_admin,
                target_type='job_title',
                target_id=job_title_id,
            ).exists()
        )


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

    def test_hr_administrator_can_update_a_job_title_name(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.patch(_detail_url(self.job_title.pk), {'name': 'Senior Software Engineer'})

        self.assertEqual(response.status_code, 200)
        self.job_title.refresh_from_db()
        self.assertEqual(self.job_title.name, 'Senior Software Engineer')

    def test_updating_to_a_duplicate_name_is_rejected(self):
        JobTitle.objects.create(name='Accountant')
        self.client.force_authenticate(self.hr_admin)

        response = self.client.patch(_detail_url(self.job_title.pk), {'name': 'Accountant'})

        self.assertEqual(response.status_code, 400)

    def test_read_only_fields_are_ignored_on_update(self):
        self.client.force_authenticate(self.hr_admin)
        original_created_at = self.job_title.created_at

        response = self.client.patch(_detail_url(self.job_title.pk), {'created_at': '2000-01-01T00:00:00Z'})

        self.assertEqual(response.status_code, 200)
        self.job_title.refresh_from_db()
        self.assertEqual(self.job_title.created_at, original_created_at)

    def test_unknown_job_title_returns_404(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.patch(_detail_url(999999), {'is_active': False})

        self.assertEqual(response.status_code, 404)

    def test_anonymous_cannot_update(self):
        response = self.client.patch(_detail_url(self.job_title.pk), {'is_active': False})

        self.assertEqual(response.status_code, 401)

    def test_updating_a_job_title_records_an_audit_log_entry(self):
        self.client.force_authenticate(self.hr_admin)

        self.client.patch(_detail_url(self.job_title.pk), {'is_active': False})

        self.assertTrue(
            AuditLog.objects.filter(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='job_title_updated',
                actor=self.hr_admin,
                target_type='job_title',
                target_id=self.job_title.pk,
            ).exists()
        )
