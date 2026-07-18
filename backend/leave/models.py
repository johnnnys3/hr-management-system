from django.conf import settings
from django.db import models

from employees.models import Employee


class LeaveType(models.Model):
    """`leave_type`, `docs/05-database-schema.md` §4.10. HRMS-FR-066."""

    name = models.CharField(max_length=255, unique=True)
    requires_approval = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leave_type'

    def __str__(self):
        return self.name


class LeaveBalance(models.Model):
    """`leave_balance`, `docs/05-database-schema.md` §4.10. HRMS-FR-065.
    `used_days` is incremented only on leave-request approval
    (HRMS-BR-010), never on request or rejection (HRMS-BR-011)."""

    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.RESTRICT, related_name='balances')
    period_start = models.DateField()
    period_end = models.DateField()
    entitled_days = models.DecimalField(max_digits=6, decimal_places=2)
    used_days = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leave_balance'
        constraints = [
            models.CheckConstraint(check=models.Q(entitled_days__gte=0), name='leave_balance_entitled_days_gte_0'),
            models.CheckConstraint(check=models.Q(used_days__gte=0), name='leave_balance_used_days_gte_0'),
            models.UniqueConstraint(
                fields=['employee', 'leave_type', 'period_start'], name='leave_balance_unique_period'
            ),
        ]

    def __str__(self):
        return f'{self.employee_id} / {self.leave_type_id} / {self.period_start}'


class LeaveRequest(models.Model):
    """`leave_request`, `docs/05-database-schema.md` §4.10. HRMS-FR-063,
    HRMS-FR-064, HRMS-BR-009 to HRMS-BR-011, HRMS-DR-006."""

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.RESTRICT, related_name='requests')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'leave_request'
        constraints = [
            models.CheckConstraint(check=models.Q(end_date__gte=models.F('start_date')), name='leave_request_end_after_start'),
        ]

    def __str__(self):
        return f'{self.employee_id} {self.leave_type_id} {self.start_date}..{self.end_date} ({self.status})'
