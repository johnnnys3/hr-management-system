"""`docs/08-testing-plan.md` §7.1: the buildable-now half of HRMS-NFR-001
to HRMS-NFR-005 — a wall-clock timing mechanism, not a threshold check.

TBD-016 (organisation size/data volumes) and TBD-017 (payroll elapsed-time
threshold) are open and not resolvable by this project (`docs/02-project-
plan.md` §8.1) — nothing here asserts a request completed within any bound.
Per §7.1's own instruction, "a performance figure measured against a
dataset this project invented is a measurement of that dataset ... not
evidence that HRMS-NFR-001 to HRMS-NFR-005 are met" — every test below
records its own fixture size in its output for exactly that reason, and
the mechanism is retained rather than deleted so a real threshold can be
plugged in the moment TBD-016/017 close, without redesigning how the
timing is taken.

HRMS-NFR-005 (payroll elapsed time) is deliberately not duplicated here:
M16's calculate/finalize Celery tasks are timed per run as a matter of
course by payroll's own async poll-to-completion tests (§7.1's own
instruction), and this module does not re-time what those already do.
"""
import time

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

from departments.models import Department, JobTitle
from employees.models import Employee
from iam.roles import HR_ADMINISTRATOR

User = get_user_model()

# Arbitrary and small — no data volume is specified anywhere (TBD-016)
# until the organisation this system is built for exists. Recorded in
# every test's own failure/print output, per the module docstring above.
FIXTURE_EMPLOYEE_COUNT = 200


class NfrTimingTests(APITestCase):
    """One test per HRMS-NFR-001 to -004, each timing a single request
    against `FIXTURE_EMPLOYEE_COUNT` fixture employees and reporting the
    elapsed time — the mechanism, not a pass/fail bound."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        department = Department.objects.create(name='NFR Timing Dept')
        job_title = JobTitle.objects.create(name='NFR Timing Role')
        Employee.objects.bulk_create(
            [
                Employee(
                    employee_number=f'NFR-{i}', first_name=f'First{i}', last_name=f'Last{i}',
                    date_of_birth='1990-01-01', department=department, job_title=job_title,
                    hire_date='2020-01-01',
                )
                for i in range(FIXTURE_EMPLOYEE_COUNT)
            ],
        )
        cls.sample_employee_id = Employee.objects.filter(employee_number='NFR-0').values_list('id', flat=True).first()

    def setUp(self):
        user = User.objects.create_user(email='nfr-timing@example.com', password='x')
        user.groups.add(Group.objects.get(name=HR_ADMINISTRATOR))
        self.client.force_authenticate(user)

    def _timed_get(self, url):
        start = time.perf_counter()
        response = self.client.get(url)
        elapsed = time.perf_counter() - start
        self.assertEqual(response.status_code, 200)
        return elapsed

    def test_hrms_nfr_001_common_page_load(self):
        """"Common pages" — the SPA's own landing call, `/api/auth/me/`."""
        elapsed = self._timed_get('/api/auth/me/')
        print(f'\nHRMS-NFR-001 (common page, /api/auth/me/): {elapsed:.3f}s against {FIXTURE_EMPLOYEE_COUNT} employees')

    def test_hrms_nfr_002_employee_search(self):
        elapsed = self._timed_get('/api/employees/?search=First1')
        print(f'\nHRMS-NFR-002 (employee search): {elapsed:.3f}s against {FIXTURE_EMPLOYEE_COUNT} employees')

    def test_hrms_nfr_003_employee_profile_page(self):
        elapsed = self._timed_get(f'/api/employees/{self.sample_employee_id}/')
        print(f'\nHRMS-NFR-003 (employee profile page): {elapsed:.3f}s against {FIXTURE_EMPLOYEE_COUNT} employees')

    def test_hrms_nfr_004_report_load(self):
        elapsed = self._timed_get('/api/reports/headcount/')
        print(f'\nHRMS-NFR-004 (report load, headcount): {elapsed:.3f}s against {FIXTURE_EMPLOYEE_COUNT} employees')
