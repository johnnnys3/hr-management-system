"""`leave_type`, `leave_balance`, `leave_request`, `docs/05-database-schema.md` §4.10."""
from datetime import date

from django.db import IntegrityError, transaction
from django.test import TestCase

from ..models import LeaveBalance, LeaveRequest, LeaveType
from .helpers import annual_leave_type, make_employee


class LeaveTypeSeedTests(TestCase):
    def test_five_canonical_types_seeded(self):
        names = set(LeaveType.objects.values_list('name', flat=True))
        self.assertEqual(
            names, {'Annual leave', 'Sick leave', 'Maternity leave', 'Study leave', 'Other'}
        )


class LeaveRequestConstraintTests(TestCase):
    def test_end_date_before_start_date_is_rejected(self):
        employee = make_employee('E-1', 'Grace', 'Hopper')
        with self.assertRaises(IntegrityError), transaction.atomic():
            LeaveRequest.objects.create(
                employee=employee, leave_type=annual_leave_type(),
                start_date=date(2026, 8, 10), end_date=date(2026, 8, 1),
            )


class LeaveBalanceConstraintTests(TestCase):
    def test_unique_per_employee_leave_type_period(self):
        employee = make_employee('E-1', 'Grace', 'Hopper')
        LeaveBalance.objects.create(
            employee=employee, leave_type=annual_leave_type(),
            period_start=date(2026, 1, 1), period_end=date(2026, 12, 31), entitled_days=15,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            LeaveBalance.objects.create(
                employee=employee, leave_type=annual_leave_type(),
                period_start=date(2026, 1, 1), period_end=date(2026, 12, 31), entitled_days=15,
            )
