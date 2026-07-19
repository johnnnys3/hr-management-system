"""Read-only aggregation queries for the five report types,
`docs/06-api-contracts.md` §4.15. Each function takes a `scope`
('full', 'team', or 'aggregate', from `permissions.report_scope`/
`payroll_report_scope`) and returns `{'aggregate': {...}}` for
Executive, or `{'aggregate': {...}, 'breakdown': [...]}` for HR/
Payroll Officer/Manager — the aggregate section is always present so
callers never have to special-case its absence, only Executive's
missing `breakdown`. HRMS-FR-053 filters (department, date range,
employment status) are plain queryset filters, not a new access
decision — narrowing what a caller can already see, never widening it.
"""
from django.db.models import Count, Q, Sum

from employees.models import Employee, EmploymentHistory
from leave.models import LeaveBalance
from payroll.models import PayrollRun, Payslip
from reporting_structure.models import ReportingRelationship

TERMINAL_STATUSES = [Employee.STATUS_TERMINATED, Employee.STATUS_RESIGNED, Employee.STATUS_RETIRED]


def _team_employee_ids(user):
    return ReportingRelationship.objects.filter(manager_employee_id=user.employee_id).values_list('employee_id', flat=True)


def headcount_report(scope, user, department_id=None, employment_status=None):
    qs = Employee.objects.all()
    if scope == 'team':
        qs = qs.filter(pk__in=_team_employee_ids(user))
    if department_id:
        qs = qs.filter(department_id=department_id)
    if employment_status:
        qs = qs.filter(employment_status=employment_status)

    result = {'aggregate': {'total': qs.count()}}
    if scope in ('full', 'team'):
        result['breakdown'] = list(
            qs.values('department_id', 'department__name', 'employment_status')
            .annotate(count=Count('id'))
            .order_by('department__name', 'employment_status'),
        )
    return result


def leave_utilization_report(scope, user, department_id=None, leave_type_id=None, period_start=None, period_end=None):
    qs = LeaveBalance.objects.all()
    if scope == 'team':
        qs = qs.filter(employee_id__in=_team_employee_ids(user))
    if department_id:
        qs = qs.filter(employee__department_id=department_id)
    if leave_type_id:
        qs = qs.filter(leave_type_id=leave_type_id)
    if period_start:
        qs = qs.filter(period_end__gte=period_start)
    if period_end:
        qs = qs.filter(period_start__lte=period_end)

    totals = qs.aggregate(entitled_days=Sum('entitled_days'), used_days=Sum('used_days'))
    result = {'aggregate': {
        'entitled_days': totals['entitled_days'] or 0,
        'used_days': totals['used_days'] or 0,
    }}
    if scope in ('full', 'team'):
        result['breakdown'] = list(
            qs.values('leave_type_id', 'leave_type__name')
            .annotate(entitled_days=Sum('entitled_days'), used_days=Sum('used_days'))
            .order_by('leave_type__name'),
        )
    return result


def turnover_report(scope, user, department_id, period_start, period_end):
    hires_qs = Employee.objects.filter(hire_date__gte=period_start, hire_date__lte=period_end)
    terminations_qs = EmploymentHistory.objects.filter(
        event_type=EmploymentHistory.EVENT_STATUS_CHANGE,
        effective_date__gte=period_start,
        effective_date__lte=period_end,
        new_value__employment_status__in=TERMINAL_STATUSES,
    )
    if scope == 'team':
        team_ids = list(_team_employee_ids(user))
        hires_qs = hires_qs.filter(pk__in=team_ids)
        terminations_qs = terminations_qs.filter(employee_id__in=team_ids)
    if department_id:
        hires_qs = hires_qs.filter(department_id=department_id)
        terminations_qs = terminations_qs.filter(employee__department_id=department_id)

    result = {'aggregate': {'hires': hires_qs.count(), 'terminations': terminations_qs.count()}}
    if scope in ('full', 'team'):
        result['breakdown'] = {
            'hires_by_department': list(
                hires_qs.values('department_id', 'department__name').annotate(count=Count('id')).order_by('department__name'),
            ),
            'terminations_by_department': list(
                terminations_qs.values('employee__department_id', 'employee__department__name')
                .annotate(count=Count('id')).order_by('employee__department__name'),
            ),
        }
    return result


def payroll_cost_report(scope, payroll_run_id=None, period_start=None, period_end=None):
    qs = Payslip.objects.all()
    if payroll_run_id:
        qs = qs.filter(payroll_run_id=payroll_run_id)
    if period_start:
        qs = qs.filter(payroll_run__period_end__gte=period_start)
    if period_end:
        qs = qs.filter(payroll_run__period_start__lte=period_end)

    totals = qs.aggregate(gross_pay=Sum('gross_pay'), net_pay=Sum('net_pay'))
    result = {'aggregate': {
        'gross_pay': totals['gross_pay'] or 0,
        'net_pay': totals['net_pay'] or 0,
    }}
    if scope == 'full':
        result['breakdown'] = list(
            qs.values('employee__department_id', 'employee__department__name')
            .annotate(gross_pay=Sum('gross_pay'), net_pay=Sum('net_pay'))
            .order_by('employee__department__name'),
        )
    return result


def payroll_summary_report(scope, payroll_run_id=None, period_start=None, period_end=None):
    qs = PayrollRun.objects.filter(status=PayrollRun.STATUS_FINALIZED)
    if payroll_run_id:
        qs = qs.filter(pk=payroll_run_id)
    if period_start:
        qs = qs.filter(period_end__gte=period_start)
    if period_end:
        qs = qs.filter(period_start__lte=period_end)

    totals = qs.aggregate(
        gross_pay=Sum('payslips__gross_pay'), net_pay=Sum('payslips__net_pay'), payslip_count=Count('payslips'),
    )
    result = {'aggregate': {
        'gross_pay': totals['gross_pay'] or 0,
        'net_pay': totals['net_pay'] or 0,
        'payslip_count': totals['payslip_count'] or 0,
    }}
    if scope == 'full':
        result['breakdown'] = list(
            qs.annotate(gross_pay=Sum('payslips__gross_pay'), net_pay=Sum('payslips__net_pay'))
            .values('id', 'period_start', 'period_end', 'gross_pay', 'net_pay')
            .order_by('period_start'),
        )
    return result


REPORT_BUILDERS = {
    'headcount': headcount_report,
    'leave_utilization': leave_utilization_report,
    'turnover': turnover_report,
    'payroll_cost': payroll_cost_report,
    'payroll_summary': payroll_summary_report,
}
