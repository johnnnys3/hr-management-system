from django.conf import settings
from django.db import models


class ReportExport(models.Model):
    """`report_export`, `docs/05-database-schema.md` §4.13. HRMS-FR-054.
    `job_id` in `docs/06-api-contracts.md` §4.15's export/poll pair is
    this table's PK — Reports otherwise owns no storage of its own, but
    the async export job itself has no other row to attach its state
    to, unlike Payroll's `calculate`/`finalize` which poll
    `payroll_run.status` directly."""

    REPORT_HEADCOUNT = 'headcount'
    REPORT_LEAVE_UTILIZATION = 'leave_utilization'
    REPORT_TURNOVER = 'turnover'
    REPORT_PAYROLL_COST = 'payroll_cost'
    REPORT_PAYROLL_SUMMARY = 'payroll_summary'
    REPORT_TYPE_CHOICES = [
        (REPORT_HEADCOUNT, 'Headcount'),
        (REPORT_LEAVE_UTILIZATION, 'Leave utilization'),
        (REPORT_TURNOVER, 'Turnover'),
        (REPORT_PAYROLL_COST, 'Payroll cost'),
        (REPORT_PAYROLL_SUMMARY, 'Payroll summary'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_COMPLETE = 'complete'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETE, 'Complete'),
        (STATUS_FAILED, 'Failed'),
    ]

    report_type = models.CharField(max_length=32, choices=REPORT_TYPE_CHOICES)
    params = models.JSONField(default=dict, blank=True)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name='report_exports')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    object_key = models.CharField(max_length=512, null=True, blank=True, unique=True)
    failed_reason = models.TextField(null=True, blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'report_export'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status='complete') | (models.Q(object_key__isnull=True) & models.Q(generated_at__isnull=True)),
                name='report_export_complete_fields',
            ),
            models.CheckConstraint(
                condition=models.Q(status='failed') | models.Q(failed_reason__isnull=True),
                name='report_export_failed_reason',
            ),
        ]

    def __str__(self):
        return f'{self.report_type} / {self.status} ({self.pk})'
