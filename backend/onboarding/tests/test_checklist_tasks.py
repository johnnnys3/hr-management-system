"""`/api/onboarding-checklists/{id}/` and `.../tasks/`, `docs/06-api-contracts.md` §4.7."""
from rest_framework.test import APITestCase

from departments.models import Department, JobTitle
from employees.models import Employee
from iam.roles import HR_ADMINISTRATOR, HR_OFFICER, RECRUITER
from notifications.models import Notification
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


class OnboardingChecklistListTests(APITestCase):
    def setUp(self):
        self.hr_officer = user_with_role('hro-list@example.com', HR_OFFICER)
        department = Department.objects.create(name='Engineering')
        job_title = JobTitle.objects.create(name='Engineer')
        self.employee = Employee.objects.create(
            employee_number='EMP-3003', first_name='Katherine', last_name='Johnson',
            date_of_birth='1918-08-26', department=department, job_title=job_title, hire_date='2026-08-01',
        )
        self.checklist = OnboardingChecklist.objects.create(employee=self.employee)
        other_employee = Employee.objects.create(
            employee_number='EMP-3004', first_name='Dorothy', last_name='Vaughan',
            date_of_birth='1910-09-20', department=department, job_title=job_title, hire_date='2026-08-01',
        )
        OnboardingChecklist.objects.create(employee=other_employee)

    def test_filters_by_employee_id(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.get('/api/onboarding-checklists/', {'employee_id': self.employee.pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual([row['id'] for row in response.data], [self.checklist.pk])

    def test_with_no_filter_returns_all_visible_checklists(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.get('/api/onboarding-checklists/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_recruiter_can_list(self):
        recruiter = user_with_role('recruiter-list@example.com', RECRUITER)
        self.client.force_authenticate(recruiter)

        response = self.client.get('/api/onboarding-checklists/', {'employee_id': self.employee.pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual([row['id'] for row in response.data], [self.checklist.pk])

    def test_anonymous_is_denied(self):
        response = self.client.get('/api/onboarding-checklists/')

        self.assertEqual(response.status_code, 401)


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
        first_response = self.client.patch(
            f'/api/onboarding-checklists/{self.checklist.pk}/tasks/{task.pk}/', {'status': 'completed'},
        )
        self.assertEqual(first_response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.status, OnboardingTask.STATUS_COMPLETED)
        self.assertEqual(task.completed_by, self.hr_officer)
        self.assertIsNotNone(task.completed_at)

        response = self.client.patch(
            f'/api/onboarding-checklists/{self.checklist.pk}/tasks/{task.pk}/', {'status': 'in_progress'},
        )

        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.status, OnboardingTask.STATUS_IN_PROGRESS)
        self.assertIsNone(task.completed_by)
        self.assertIsNone(task.completed_at)

    def test_creating_a_task_notifies_the_employee_if_they_have_a_user_account(self):
        employee_user = user_with_role('grace@example.com', HR_OFFICER)
        employee_user.employee = self.checklist.employee
        employee_user.save(update_fields=['employee'])
        self.client.force_authenticate(self.hr_officer)

        response = self.client.post(
            f'/api/onboarding-checklists/{self.checklist.pk}/tasks/', {'name': 'IT provisioning'},
        )

        self.assertEqual(response.status_code, 201)
        task = OnboardingTask.objects.get(pk=response.data['id'])
        notification = Notification.objects.get(related_type='onboarding_task', related_id=task.pk)
        self.assertEqual(notification.recipient_id, employee_user.pk)
        self.assertEqual(notification.category, Notification.CATEGORY_PENDING_TASK)

    def test_creating_a_task_does_not_error_when_the_employee_has_no_user_account(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.post(
            f'/api/onboarding-checklists/{self.checklist.pk}/tasks/', {'name': 'IT provisioning'},
        )

        self.assertEqual(response.status_code, 201)
        task = OnboardingTask.objects.get(pk=response.data['id'])
        self.assertFalse(Notification.objects.filter(related_type='onboarding_task', related_id=task.pk).exists())

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
        self.assertIsNone(task.completed_at)
