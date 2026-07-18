"""`/api/employees/`, `docs/06-api-contracts.md` §4.3 and
`docs/07-iam-rbac.md` §4.2's Employee records row."""
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

from departments.models import Department, JobTitle
from employees.models import Employee, EmploymentHistory
from iam.roles import HR_ADMINISTRATOR, HR_OFFICER, PAYROLL_OFFICER, RECRUITER

User = get_user_model()

EMPLOYEES_URL = '/api/employees/'


def _detail_url(pk):
    return f'/api/employees/{pk}/'


def _user_with_role(email, role_name):
    user = User.objects.create_user(email=email, password='x')
    user.groups.add(Group.objects.get(name=role_name))
    return user


def _employee_payload(**overrides):
    department = overrides.pop('department', None) or Department.objects.create(name='Engineering')
    job_title = overrides.pop('job_title', None) or JobTitle.objects.create(name='Engineer')
    payload = {
        'employee_number': 'E-1001',
        'first_name': 'Ada',
        'last_name': 'Lovelace',
        'date_of_birth': '1990-01-01',
        'department': department.pk,
        'job_title': job_title.pk,
        'hire_date': str(date.today()),
    }
    payload.update(overrides)
    return payload


class EmployeeListCreateTests(APITestCase):
    def setUp(self):
        self.hr_officer = _user_with_role('hrofficer@example.com', HR_OFFICER)
        self.hr_admin = _user_with_role('hradmin@example.com', HR_ADMINISTRATOR)

    def test_hr_officer_can_create_an_employee(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.post(EMPLOYEES_URL, _employee_payload())

        self.assertEqual(response.status_code, 201)
        employee = Employee.objects.get(employee_number='E-1001')
        self.assertEqual(employee.employment_status, Employee.STATUS_ACTIVE)
        self.assertTrue(EmploymentHistory.objects.filter(employee=employee, event_type=EmploymentHistory.EVENT_HIRED).exists())

    def test_employment_status_is_not_client_settable_at_creation(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.post(EMPLOYEES_URL, _employee_payload(employment_status='terminated'))

        self.assertEqual(response.status_code, 201)
        employee = Employee.objects.get(employee_number='E-1001')
        self.assertEqual(employee.employment_status, Employee.STATUS_ACTIVE)

    def test_hr_administrator_cannot_create_an_employee(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.post(EMPLOYEES_URL, _employee_payload())

        self.assertEqual(response.status_code, 403)

    def test_recruiter_and_payroll_officer_cannot_create_an_employee(self):
        department = Department.objects.create(name='Engineering')
        job_title = JobTitle.objects.create(name='Engineer')
        for role in (RECRUITER, PAYROLL_OFFICER):
            user = _user_with_role(f'{role.lower().replace(" ", "")}@example.com', role)
            self.client.force_authenticate(user)

            response = self.client.post(
                EMPLOYEES_URL,
                _employee_payload(employee_number=f'E-{role}', department=department, job_title=job_title),
            )

            self.assertEqual(response.status_code, 403)

    def test_future_date_of_birth_is_rejected(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.post(EMPLOYEES_URL, _employee_payload(date_of_birth=str(date.today() + timedelta(days=1))))

        self.assertEqual(response.status_code, 400)

    def test_future_hire_date_is_rejected(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.post(EMPLOYEES_URL, _employee_payload(hire_date=str(date.today() + timedelta(days=1))))

        self.assertEqual(response.status_code, 400)

    def test_hr_officer_and_hr_administrator_see_all_employees(self):
        department = Department.objects.create(name='Engineering')
        job_title = JobTitle.objects.create(name='Engineer')
        Employee.objects.create(
            employee_number='E-1', first_name='Ada', last_name='Lovelace',
            date_of_birth='1990-01-01', department=department, job_title=job_title,
            hire_date=date.today(),
        )

        for user in (self.hr_officer, self.hr_admin):
            self.client.force_authenticate(user)
            response = self.client.get(EMPLOYEES_URL)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data), 1)

    def test_anonymous_is_denied(self):
        response = self.client.get(EMPLOYEES_URL)

        self.assertEqual(response.status_code, 401)

    def test_employee_with_no_other_role_sees_only_own_record(self):
        department = Department.objects.create(name='Engineering')
        job_title = JobTitle.objects.create(name='Engineer')
        own = Employee.objects.create(
            employee_number='E-1', first_name='Ada', last_name='Lovelace',
            date_of_birth='1990-01-01', department=department, job_title=job_title,
            hire_date=date.today(),
        )
        Employee.objects.create(
            employee_number='E-2', first_name='Grace', last_name='Hopper',
            date_of_birth='1990-01-01', department=department, job_title=job_title,
            hire_date=date.today(),
        )
        user = User.objects.create_user(email='ada@example.com', password='x', employee=own)
        self.client.force_authenticate(user)

        response = self.client.get(EMPLOYEES_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['employee_number'], 'E-1')

    def test_user_with_no_employee_record_and_no_role_is_forbidden(self):
        user = User.objects.create_user(email='nobody@example.com', password='x')
        self.client.force_authenticate(user)

        response = self.client.get(EMPLOYEES_URL)

        self.assertEqual(response.status_code, 403)

    def test_manager_sees_own_record_and_direct_reports_only(self):
        """Module 8 (Reporting Structure)'s `_visible_employees` Manager
        branch: not the same as Employee's "own record only" — a Manager
        additionally sees their direct reports, and nothing beyond that."""
        from reporting_structure.models import ReportingRelationship

        department = Department.objects.create(name='Engineering')
        job_title = JobTitle.objects.create(name='Engineer')
        manager = Employee.objects.create(
            employee_number='E-1', first_name='Ada', last_name='Lovelace',
            date_of_birth='1990-01-01', department=department, job_title=job_title, hire_date=date.today(),
        )
        report = Employee.objects.create(
            employee_number='E-2', first_name='Grace', last_name='Hopper',
            date_of_birth='1990-01-01', department=department, job_title=job_title, hire_date=date.today(),
        )
        unrelated = Employee.objects.create(
            employee_number='E-3', first_name='Alan', last_name='Turing',
            date_of_birth='1990-01-01', department=department, job_title=job_title, hire_date=date.today(),
        )
        ReportingRelationship.objects.create(employee=report, manager_employee=manager, effective_from=date.today())
        user = User.objects.create_user(email='ada@example.com', password='x', employee=manager)
        self.client.force_authenticate(user)

        response = self.client.get(EMPLOYEES_URL)

        self.assertEqual(response.status_code, 200)
        seen = {row['employee_number'] for row in response.data}
        self.assertEqual(seen, {'E-1', 'E-2'})
        self.assertNotIn(unrelated.employee_number, seen)

    def test_terminated_employee_loses_access(self):
        department = Department.objects.create(name='Engineering')
        job_title = JobTitle.objects.create(name='Engineer')
        own = Employee.objects.create(
            employee_number='E-1', first_name='Ada', last_name='Lovelace',
            date_of_birth='1990-01-01', department=department, job_title=job_title,
            hire_date=date.today(), employment_status=Employee.STATUS_TERMINATED,
        )
        user = User.objects.create_user(email='ada@example.com', password='x', employee=own)
        self.client.force_authenticate(user)

        response = self.client.get(EMPLOYEES_URL)

        self.assertEqual(response.status_code, 403)


class EmployeeDetailTests(APITestCase):
    def setUp(self):
        self.hr_officer = _user_with_role('hrofficer@example.com', HR_OFFICER)
        self.hr_admin = _user_with_role('hradmin@example.com', HR_ADMINISTRATOR)
        self.department = Department.objects.create(name='Engineering')
        self.other_department = Department.objects.create(name='Sales')
        self.job_title = JobTitle.objects.create(name='Engineer')
        self.employee = Employee.objects.create(
            employee_number='E-1', first_name='Ada', last_name='Lovelace',
            date_of_birth='1990-01-01', department=self.department, job_title=self.job_title,
            hire_date=date.today(),
        )

    def test_hr_officer_can_update_the_full_record(self):
        self.client.force_authenticate(self.hr_officer)

        response = self.client.patch(_detail_url(self.employee.pk), {'department': self.other_department.pk})

        self.assertEqual(response.status_code, 200)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.department_id, self.other_department.pk)
        self.assertTrue(
            EmploymentHistory.objects.filter(employee=self.employee, event_type=EmploymentHistory.EVENT_DEPARTMENT_CHANGE).exists()
        )

    def test_hr_administrator_can_update_status_only(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.patch(_detail_url(self.employee.pk), {'employment_status': 'on_leave'})

        self.assertEqual(response.status_code, 200)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.employment_status, 'on_leave')
        self.assertTrue(
            EmploymentHistory.objects.filter(employee=self.employee, event_type=EmploymentHistory.EVENT_STATUS_CHANGE).exists()
        )

    def test_hr_administrator_cannot_update_department(self):
        self.client.force_authenticate(self.hr_admin)

        response = self.client.patch(_detail_url(self.employee.pk), {'department': self.other_department.pk})

        self.assertEqual(response.status_code, 200)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.department_id, self.department.pk)

    def test_employee_cannot_see_a_record_that_is_not_their_own(self):
        other = Employee.objects.create(
            employee_number='E-2', first_name='Grace', last_name='Hopper',
            date_of_birth='1990-01-01', department=self.department, job_title=self.job_title,
            hire_date=date.today(),
        )
        user = User.objects.create_user(email='ada@example.com', password='x', employee=self.employee)
        self.client.force_authenticate(user)

        response = self.client.get(_detail_url(other.pk))

        self.assertEqual(response.status_code, 404)


class EmployeeSelfServiceTests(APITestCase):
    def setUp(self):
        self.department = Department.objects.create(name='Engineering')
        self.job_title = JobTitle.objects.create(name='Engineer')
        self.employee = Employee.objects.create(
            employee_number='E-1', first_name='Ada', last_name='Lovelace',
            date_of_birth='1990-01-01', department=self.department, job_title=self.job_title,
            hire_date=date.today(),
        )
        self.user = User.objects.create_user(email='ada@example.com', password='x', employee=self.employee)

    def test_employee_can_read_own_profile(self):
        self.client.force_authenticate(self.user)

        response = self.client.get('/api/employees/me/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['employee_number'], 'E-1')

    def test_employee_cannot_write_master_fields_via_self_service(self):
        other_department = Department.objects.create(name='Sales')
        self.client.force_authenticate(self.user)

        response = self.client.patch('/api/employees/me/', {
            'department': other_department.pk,
            'employment_status': 'terminated',
        })

        self.assertEqual(response.status_code, 200)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.department_id, self.department.pk)
        self.assertEqual(self.employee.employment_status, Employee.STATUS_ACTIVE)

    def test_hr_officer_cannot_use_the_self_service_endpoint(self):
        hr_officer = _user_with_role('hrofficer@example.com', HR_OFFICER)
        self.client.force_authenticate(hr_officer)

        response = self.client.get('/api/employees/me/')

        self.assertEqual(response.status_code, 403)

    def test_user_with_no_employee_record_is_forbidden(self):
        user = User.objects.create_user(email='nobody@example.com', password='x')
        self.client.force_authenticate(user)

        response = self.client.get('/api/employees/me/')

        self.assertEqual(response.status_code, 403)
