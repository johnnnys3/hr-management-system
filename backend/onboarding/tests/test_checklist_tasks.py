"""`/api/onboarding-checklists/{id}/` and `.../tasks/`, `docs/06-api-contracts.md` §4.7."""
from rest_framework.test import APITestCase

from departments.models import Department, JobTitle
from employees.models import Employee
from iam.roles import HR_ADMINISTRATOR, HR_OFFICER, RECRUITER
from onboarding.models import OnboardingChecklist, OnboardingTask

from .helpers import user_with_role


class OnboardingChecklistDetailTests(APITestCase):
    def setUp(self):
        self.hr_officer = user_with_role('hro@example.com', HR_OFFICER)
        department = Department.objects.create(name='Engineering')
        job_title = JobTitle.objects.create(name='Engineer')
        employee = Employee.objects.create(
            employee_number='EMP-3001', first_name='Ada', last_name='Lovelace',
            date_of_birth='1988-05-05', department=department, job_title=job_title, hire_date='2026-08-01',
        )
        self.checklist = OnboardingChecklist.objects.create(employee=employee)

    def test_hr_officer_recruiter_and_hr_administrator_can_read(self):
        for role in [HR_OFFICER, HR_ADMINISTRATOR, RECRUITER]:
            user = user_with_role(f'{role}@example.com', role)
            self.client.force_authenticate(user)

            response = self.client.get(f'/api/onboarding-checklists/{self.checklist.pk}/')

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['id'], self.checklist.pk)


class OnboardingTaskTests(APITestCase):
    def setUp(self):
        self.hr_officer = user_with_role('hro@example.com', HR_OFFICER)
        department = Department.objects.create(name='Engineering')
        job_title = JobTitle.objects.create(name='Engineer')
        employee = Employee.objects.create(
            employee_number='EMP-3002', first_name='Grace', last_name='Hopper',
            date_of_birth='1906-12-09', department=department, job_title=job_title, hire_date='2026-08-01',
        )
        self.checklist = OnboardingChecklist.objects.create(employee=employee)

    def test_hr_officer_can_create_and_list_tasks(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.post(
            f'/api/onboarding-checklists/{self.checklist.pk}/tasks/', {'name': 'IT provisioning'},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], OnboardingTask.STATUS_PENDING)

        list_response = self.client.get(f'/api/onboarding-checklists/{self.checklist.pk}/tasks/')
        self.assertEqual(len(list_response.data), 1)

    def test_recruiter_cannot_create_a_task(self):
        recruiter = user_with_role('recruiter@example.com', RECRUITER)
        self.client.force_authenticate(recruiter)

        response = self.client.post(
            f'/api/onboarding-checklists/{self.checklist.pk}/tasks/', {'name': 'IT provisioning'},
        )

        self.assertEqual(response.status_code, 403)

    def test_recruiter_can_list_tasks(self):
        OnboardingTask.objects.create(checklist=self.checklist, name='IT provisioning')
        recruiter = user_with_role('recruiter2@example.com', RECRUITER)
        self.client.force_authenticate(recruiter)

        response = self.client.get(f'/api/onboarding-checklists/{self.checklist.pk}/tasks/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_patching_status_to_completed_sets_completed_by_and_completed_at(self):
        task = OnboardingTask.objects.create(checklist=self.checklist, name='IT provisioning')
        self.client.force_authenticate(self.hr_officer)

        response = self.client.patch(
            f'/api/onboarding-checklists/{self.checklist.pk}/tasks/{task.pk}/', {'status': 'completed'},
        )

        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.status, OnboardingTask.STATUS_COMPLETED)
        self.assertEqual(task.completed_by, self.hr_officer)
        self.assertIsNotNone(task.completed_at)

    def test_transitioning_away_from_completed_clears_completion_metadata(self):
        task = OnboardingTask.objects.create(checklist=self.checklist, name='IT provisioning')
        self.client.force_authenticate(self.hr_officer)
        self.client.patch(
            f'/api/onboarding-checklists/{self.checklist.pk}/tasks/{task.pk}/', {'status': 'completed'},
        )

        response = self.client.patch(
            f'/api/onboarding-checklists/{self.checklist.pk}/tasks/{task.pk}/', {'status': 'in_progress'},
        )

        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.status, OnboardingTask.STATUS_IN_PROGRESS)
        self.assertIsNone(task.completed_by)
        self.assertIsNone(task.completed_at)

    def test_creating_a_task_ignores_a_client_supplied_status(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.post(
            f'/api/onboarding-checklists/{self.checklist.pk}/tasks/',
            {'name': 'IT provisioning', 'status': 'completed'},
        )

        self.assertEqual(response.status_code, 201)
        task = OnboardingTask.objects.get(pk=response.data['id'])
        self.assertEqual(task.status, OnboardingTask.STATUS_PENDING)
        self.assertIsNone(task.completed_by)
