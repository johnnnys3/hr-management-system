"""`GET, POST, PATCH /api/benefits/`, `GET, POST, PATCH /api/employees/{id}/benefit-enrollments/`,
`docs/06-api-contracts.md` §4.13."""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from iam.roles import HR_ADMINISTRATOR, HR_OFFICER

from ..models import Benefit, BenefitEnrollment
from .helpers import make_employee, user_with_role

User = get_user_model()


class BenefitTests(APITestCase):
    def test_hr_administrator_can_create_and_update(self):
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))

        create = self.client.post('/api/benefits/', {'name': 'Health insurance', 'provider': 'Acme', 'cost': '100.00'})
        update = self.client.patch(f"/api/benefits/{create.data['id']}/", {'cost': '150.00'})

        self.assertEqual(create.status_code, 201)
        self.assertEqual(update.status_code, 200)

    def test_hr_officer_can_read_but_not_create(self):
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))

        response = self.client.post('/api/benefits/', {'name': 'Health insurance'})

        self.assertEqual(response.status_code, 403)


class BenefitEnrollmentTests(APITestCase):
    def setUp(self):
        self.employee = make_employee('E-1', 'Grace', 'Hopper')
        self.benefit = Benefit.objects.create(name='Health insurance')
        self.url = f'/api/employees/{self.employee.pk}/benefit-enrollments/'

    def test_hr_administrator_can_enroll(self):
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))

        response = self.client.post(self.url, {'benefit': self.benefit.pk})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'active')

    def test_employee_cannot_enroll_self(self):
        user = User.objects.create_user(email='grace@example.com', password='x', employee=self.employee)
        self.client.force_authenticate(user)

        response = self.client.post(self.url, {'benefit': self.benefit.pk})

        self.assertEqual(response.status_code, 403)

    def test_employee_can_read_own(self):
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))
        self.client.post(self.url, {'benefit': self.benefit.pk})

        user = User.objects.create_user(email='grace@example.com', password='x', employee=self.employee)
        self.client.force_authenticate(user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_employee_cannot_read_anothers_with_zero_enrollments(self):
        """A list-scoped permission check must not be skipped just
        because the target employee happens to have no rows yet."""
        other = make_employee('E-2', 'Ada', 'Lovelace')
        other_user = User.objects.create_user(email='ada@example.com', password='x', employee=other)
        self.client.force_authenticate(other_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_patch_cancel_sets_cancelled_at(self):
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))
        enrollment_id = self.client.post(self.url, {'benefit': self.benefit.pk}).data['id']

        response = self.client.patch(f'{self.url}{enrollment_id}/', {'status': 'cancelled'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'cancelled')
        self.assertIsNotNone(response.data['cancelled_at'])
        self.assertIsNotNone(BenefitEnrollment.objects.get(pk=enrollment_id).cancelled_at)

    def test_patch_to_active_is_rejected(self):
        """This endpoint only accepts the one transition it exists for."""
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))
        enrollment_id = self.client.post(self.url, {'benefit': self.benefit.pk}).data['id']

        response = self.client.patch(f'{self.url}{enrollment_id}/', {'status': 'active'})

        self.assertEqual(response.status_code, 400)

    def test_employee_cannot_patch(self):
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))
        enrollment_id = self.client.post(self.url, {'benefit': self.benefit.pk}).data['id']

        user = User.objects.create_user(email='grace@example.com', password='x', employee=self.employee)
        self.client.force_authenticate(user)
        response = self.client.patch(f'{self.url}{enrollment_id}/', {'status': 'cancelled'})

        self.assertEqual(response.status_code, 403)
