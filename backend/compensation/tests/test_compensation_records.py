"""`GET, POST /api/employees/{id}/compensation-records/`,
`docs/06-api-contracts.md` §4.13. Append-only per HRMS-DR-010/schema
§3.4: no PATCH/DELETE, a correction is a new POST superseding the prior
current row."""
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework.test import APITestCase

from iam.roles import HR_ADMINISTRATOR, HR_OFFICER, PAYROLL_OFFICER

from ..models import CompensationRecord
from .helpers import make_employee, make_pay_grade, user_with_role

User = get_user_model()


class CompensationRecordTests(APITestCase):
    def setUp(self):
        self.employee = make_employee('E-1', 'Grace', 'Hopper')
        self.pay_grade = make_pay_grade()
        self.url = f'/api/employees/{self.employee.pk}/compensation-records/'

    def test_hr_officer_can_create(self):
        officer = user_with_role('hro@example.com', HR_OFFICER)
        self.client.force_authenticate(officer)

        response = self.client.post(
            self.url, {'pay_grade': self.pay_grade.pk, 'base_salary': '1500.00', 'effective_from': '2026-01-01'}
        )

        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.data['is_superseded'])
        self.assertEqual(response.data['recorded_by'], officer.pk)

    def test_hr_administrator_cannot_create(self):
        """§4.2's 'Assign employee to pay grade' row is HR Officer only."""
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))

        response = self.client.post(
            self.url, {'pay_grade': self.pay_grade.pk, 'base_salary': '1500.00', 'effective_from': '2026-01-01'}
        )

        self.assertEqual(response.status_code, 403)

    def test_second_post_supersedes_the_first(self):
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))
        first = self.client.post(
            self.url, {'pay_grade': self.pay_grade.pk, 'base_salary': '1500.00', 'effective_from': '2026-01-01'}
        ).data

        second = self.client.post(
            self.url, {'pay_grade': self.pay_grade.pk, 'base_salary': '1800.00', 'effective_from': '2026-06-01'}
        )

        self.assertEqual(second.status_code, 201)
        self.assertFalse(second.data['is_superseded'])
        first_row = CompensationRecord.objects.get(pk=first['id'])
        self.assertTrue(first_row.is_superseded)
        self.assertEqual(str(first_row.effective_to), '2026-06-01')
        # the superseded row's own recorded values are never rewritten
        self.assertEqual(str(first_row.base_salary), '1500.00')

    def test_backdated_post_is_rejected(self):
        """api-contracts §4.13: 'a correction is a new POST with a later
        effective_from.' A backdated POST must not supersede the current
        row and invert its effective_to/effective_from ordering."""
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))
        self.client.post(
            self.url, {'pay_grade': self.pay_grade.pk, 'base_salary': '1500.00', 'effective_from': '2026-06-01'}
        )

        response = self.client.post(
            self.url, {'pay_grade': self.pay_grade.pk, 'base_salary': '1200.00', 'effective_from': '2026-01-01'}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(CompensationRecord.objects.count(), 1)
        self.assertFalse(CompensationRecord.objects.get().is_superseded)

    def test_get_returns_full_history_most_recent_first(self):
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))
        self.client.post(
            self.url, {'pay_grade': self.pay_grade.pk, 'base_salary': '1500.00', 'effective_from': '2026-01-01'}
        )
        self.client.post(
            self.url, {'pay_grade': self.pay_grade.pk, 'base_salary': '1800.00', 'effective_from': '2026-06-01'}
        )
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['effective_from'], '2026-06-01')

    def test_payroll_officer_can_read(self):
        self.client.force_authenticate(user_with_role('payroll@example.com', PAYROLL_OFFICER))

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_employee_self_read_is_denied(self):
        """§4.2's Compensation history row grants no Employee cell; own
        compensation is not exposed at `/api/employees/me/` either."""
        user = User.objects.create_user(email='grace@example.com', password='x', employee=self.employee)
        self.client.force_authenticate(user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_db_rejects_two_current_rows_for_the_same_employee(self):
        """`compensation_record_one_current_per_employee` is a
        defense-in-depth guard independent of the view's own
        select_for_update() locking — it must hold even if a caller
        bypasses the view (e.g. a data migration, a bug elsewhere)."""
        CompensationRecord.objects.create(
            employee=self.employee, pay_grade=self.pay_grade, base_salary='1500.00', effective_from='2026-01-01',
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CompensationRecord.objects.create(
                    employee=self.employee, pay_grade=self.pay_grade,
                    base_salary='1800.00', effective_from='2026-06-01',
                )

    def test_no_patch_or_delete_endpoint_exists(self):
        self.client.force_authenticate(user_with_role('hro@example.com', HR_OFFICER))
        created = self.client.post(
            self.url, {'pay_grade': self.pay_grade.pk, 'base_salary': '1500.00', 'effective_from': '2026-01-01'}
        ).data

        # HR Administrator: passes the permission check for a
        # non-GET/POST method, so this exercises "no handler exists"
        # (405) rather than "role denied" (403, covered elsewhere).
        self.client.force_authenticate(user_with_role('hra@example.com', HR_ADMINISTRATOR))
        patch = self.client.patch(self.url, {'base_salary': '9999.00'})

        self.assertEqual(patch.status_code, 405)
        self.assertEqual(CompensationRecord.objects.get(pk=created['id']).base_salary, 1500)
