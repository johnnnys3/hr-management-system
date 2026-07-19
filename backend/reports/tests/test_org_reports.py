from datetime import date

from rest_framework.test import APITestCase

from employees.models import Employee, EmploymentHistory
from iam.roles import EXECUTIVE, HR_OFFICER
from leave.tests.helpers import annual_leave_type
from reporting_structure.models import ReportingRelationship

from .helpers import make_employee, user_with_role


class HeadcountReportTests(APITestCase):
    def setUp(self):
        self.e1 = make_employee('E-1', 'Grace', 'Hopper')
        self.e2 = make_employee('E-2', 'Ada', 'Lovelace')

    def test_hr_officer_gets_full_breakdown(self):
        self.client.force_authenticate(user_with_role('hr@example.com', HR_OFFICER))

        response = self.client.get('/api/reports/headcount/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['aggregate']['total'], 2)
        self.assertIn('breakdown', response.data)

    def test_executive_gets_aggregate_only(self):
        """HRMS-NFR-019: Executive never sees a breakdown, only totals."""
        self.client.force_authenticate(user_with_role('exec@example.com', EXECUTIVE))

        response = self.client.get('/api/reports/headcount/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['aggregate']['total'], 2)
        self.assertNotIn('breakdown', response.data)

    def test_executive_who_also_holds_hr_role_still_gets_aggregate_only(self):
        """The check-Executive-first short-circuit DASH-001 established
        — an Executive who also holds HR Officer must not get the HR
        branch's full breakdown."""
        user = user_with_role('both@example.com', EXECUTIVE)
        user.groups.add(user.groups.model.objects.get(name=HR_OFFICER))
        self.client.force_authenticate(user)

        response = self.client.get('/api/reports/headcount/')

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('breakdown', response.data)

    def test_manager_gets_team_scoped_total(self):
        manager = make_employee('M-1', 'Linus', 'Torvalds')
        ReportingRelationship.objects.create(employee=self.e1, manager_employee=manager, effective_from=date.today())
        user = user_with_role('mgr@example.com', None, employee=manager)

        self.client.force_authenticate(user)
        response = self.client.get('/api/reports/headcount/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['aggregate']['total'], 1)

    def test_employee_with_no_role_is_denied(self):
        user = user_with_role('emp@example.com', None, employee=self.e1)
        self.client.force_authenticate(user)

        response = self.client.get('/api/reports/headcount/')

        self.assertEqual(response.status_code, 403)

    def test_anonymous_is_denied(self):
        response = self.client.get('/api/reports/headcount/')

        self.assertEqual(response.status_code, 401)

    def test_department_filter_narrows_scope(self):
        self.client.force_authenticate(user_with_role('hr@example.com', HR_OFFICER))

        response = self.client.get(f'/api/reports/headcount/?department_id={self.e1.department_id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['aggregate']['total'], 2)  # both seeded employees share one department


class LeaveUtilizationReportTests(APITestCase):
    def setUp(self):
        self.employee = make_employee('E-1', 'Grace', 'Hopper')
        self.leave_type = annual_leave_type()
        self.employee.leave_balances.create(
            leave_type=self.leave_type, period_start='2026-01-01', period_end='2026-12-31',
            entitled_days='20.00', used_days='5.00',
        )

    def test_hr_officer_gets_totals_and_breakdown(self):
        self.client.force_authenticate(user_with_role('hr@example.com', HR_OFFICER))

        response = self.client.get('/api/reports/leave-utilization/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(float(response.data['aggregate']['used_days']), 5.0)
        self.assertIn('breakdown', response.data)

    def test_executive_gets_aggregate_only(self):
        self.client.force_authenticate(user_with_role('exec@example.com', EXECUTIVE))

        response = self.client.get('/api/reports/leave-utilization/')

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('breakdown', response.data)


class TurnoverReportTests(APITestCase):
    def setUp(self):
        self.hired_in_period = make_employee('E-1', 'Grace', 'Hopper', )
        self.hired_in_period.hire_date = date(2026, 3, 1)
        self.hired_in_period.save(update_fields=['hire_date'])

        self.terminated = make_employee('E-2', 'Ada', 'Lovelace')
        self.terminated.employment_status = Employee.STATUS_TERMINATED
        self.terminated.save(update_fields=['employment_status'])
        EmploymentHistory.objects.create(
            employee=self.terminated, event_type=EmploymentHistory.EVENT_STATUS_CHANGE,
            effective_date=date(2026, 3, 15), new_value={'employment_status': Employee.STATUS_TERMINATED},
        )

    def test_hr_officer_sees_hires_and_terminations_in_period(self):
        self.client.force_authenticate(user_with_role('hr@example.com', HR_OFFICER))

        response = self.client.get('/api/reports/turnover/?period_start=2026-01-01&period_end=2026-06-30')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['aggregate']['hires'], 1)
        self.assertEqual(response.data['aggregate']['terminations'], 1)

    def test_missing_period_is_rejected(self):
        self.client.force_authenticate(user_with_role('hr@example.com', HR_OFFICER))

        response = self.client.get('/api/reports/turnover/')

        self.assertEqual(response.status_code, 400)

    def test_executive_gets_aggregate_only(self):
        self.client.force_authenticate(user_with_role('exec@example.com', EXECUTIVE))

        response = self.client.get('/api/reports/turnover/?period_start=2026-01-01&period_end=2026-06-30')

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('breakdown', response.data)
