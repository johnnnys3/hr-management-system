"""`GET, POST, PATCH /api/salary-structures/`, `/api/pay-grades/`,
`docs/06-api-contracts.md` §4.13."""
from datetime import date

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from iam.roles import HR_ADMINISTRATOR, HR_OFFICER, PAYROLL_OFFICER, RECRUITER

from ..models import PayGrade, SalaryStructure
from .helpers import make_employee, make_pay_grade, user_with_role

User = get_user_model()


class SalaryStructureTests(APITestCase):
    def test_hr_administrator_can_create(self):
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))

        response = self.client.post(
            '/api/salary-structures/', {'name': 'Core structure', 'effective_from': '2026-01-01'}
        )

        self.assertEqual(response.status_code, 201)

    def test_hr_officer_can_read_but_not_create(self):
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))

        read = self.client.get('/api/salary-structures/')
        write = self.client.post(
            '/api/salary-structures/', {'name': 'Core structure', 'effective_from': '2026-01-01'}
        )

        self.assertEqual(read.status_code, 200)
        self.assertEqual(write.status_code, 403)

    def test_payroll_officer_can_read(self):
        self.client.force_authenticate(user_with_role('payroll@example.com', PAYROLL_OFFICER))

        response = self.client.get('/api/salary-structures/')

        self.assertEqual(response.status_code, 200)

    def test_employee_is_denied(self):
        employee = make_employee('E-1', 'Grace', 'Hopper')
        user = User.objects.create_user(email='grace@example.com', password='x', employee=employee)
        self.client.force_authenticate(user)

        response = self.client.get('/api/salary-structures/')

        self.assertEqual(response.status_code, 403)

    def test_anonymous_is_denied(self):
        response = self.client.get('/api/salary-structures/')

        self.assertEqual(response.status_code, 401)


class PayGradeTests(APITestCase):
    def test_hr_administrator_can_create_and_update(self):
        user = user_with_role('hra@example.com', HR_ADMINISTRATOR)
        self.client.force_authenticate(user)
        structure_id = self.client.post(
            '/api/salary-structures/', {'name': 'Core structure', 'effective_from': '2026-01-01'}
        ).data['id']

        create = self.client.post(
            '/api/pay-grades/',
            {'salary_structure': structure_id, 'name': 'Grade 1', 'min_salary': '1000.00', 'max_salary': '2000.00'},
        )
        update = self.client.patch(f"/api/pay-grades/{create.data['id']}/", {'max_salary': '2500.00'})

        self.assertEqual(create.status_code, 201)
        self.assertEqual(update.status_code, 200)
        self.assertEqual(update.data['max_salary'], '2500.00')

    def test_negative_min_salary_is_rejected_with_400_not_500(self):
        """`min_salary`/`max_salary` carry a DB CheckConstraint but no
        model-level validator would leave a negative value to crash as
        an unhandled IntegrityError instead of a clean 400."""
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))
        structure_id = self.client.post(
            '/api/salary-structures/', {'name': 'Core structure', 'effective_from': '2026-01-01'}
        ).data['id']

        response = self.client.post(
            '/api/pay-grades/',
            {'salary_structure': structure_id, 'name': 'Grade 1', 'min_salary': '-100.00', 'max_salary': '2000.00'},
        )

        self.assertEqual(response.status_code, 400)

    def test_max_salary_below_min_salary_is_rejected(self):
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))
        structure_id = self.client.post(
            '/api/salary-structures/', {'name': 'Core structure', 'effective_from': '2026-01-01'}
        ).data['id']

        response = self.client.post(
            '/api/pay-grades/',
            {'salary_structure': structure_id, 'name': 'Grade 1', 'min_salary': '2000.00', 'max_salary': '1000.00'},
        )

        self.assertEqual(response.status_code, 400)

    def test_hr_officer_can_read_but_not_create(self):
        make_pay_grade()
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))

        response = self.client.get('/api/pay-grades/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_employee_is_denied(self):
        employee = make_employee('E-1', 'Grace', 'Hopper')
        user = User.objects.create_user(email='grace@example.com', password='x', employee=employee)
        self.client.force_authenticate(user)

        response = self.client.get('/api/pay-grades/')

        self.assertEqual(response.status_code, 403)

    def test_recruiter_can_read_but_not_create_and_sees_no_salary_figures(self):
        # Issue #98: Recruiter needs a blind selection of pay grades to set
        # offered_pay_grade on an offer, without compensation visibility
        # (docs/07-iam-rbac.md §2.4).
        pay_grade = make_pay_grade(name='Level 3')
        self.client.force_authenticate(user_with_role('recruiter@example.com', RECRUITER))

        read = self.client.get('/api/pay-grades/')
        write = self.client.post(
            '/api/pay-grades/',
            {'salary_structure': pay_grade.salary_structure_id, 'name': 'Level 4', 'min_salary': '1000.00', 'max_salary': '2000.00'},
        )

        self.assertEqual(read.status_code, 200)
        self.assertEqual(read.data, [{
            'id': pay_grade.pk, 'name': 'Level 3', 'salary_structure_name': pay_grade.salary_structure.name,
        }])
        self.assertEqual(write.status_code, 403)

    def test_recruiter_sees_salary_structure_name_disambiguating_same_named_grades(self):
        # Issue #107: two pay grades named alike in different salary
        # structures must render distinguishably to a Recruiter.
        engineering = SalaryStructure.objects.create(name='Engineering Ladder', effective_from=date.today())
        sales = SalaryStructure.objects.create(name='Sales Ladder', effective_from=date.today())
        PayGrade.objects.create(salary_structure=engineering, name='Level 3', min_salary='1000.00', max_salary='2000.00')
        PayGrade.objects.create(salary_structure=sales, name='Level 3', min_salary='1500.00', max_salary='2500.00')
        self.client.force_authenticate(user_with_role('recruiter2@example.com', RECRUITER))

        response = self.client.get('/api/pay-grades/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {(row['name'], row['salary_structure_name']) for row in response.data},
            {('Level 3', 'Engineering Ladder'), ('Level 3', 'Sales Ladder')},
        )
