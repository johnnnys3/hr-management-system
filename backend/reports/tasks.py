"""Celery task for `POST /api/reports/{report}/export/`,
`docs/06-api-contracts.md` §4.15: returns `202` + `job_id`, caller polls
`GET /api/report-exports/{job_id}/` for `status`. Same async shape as
Payroll's `calculate`/`finalize` (`payroll.tasks`), reused rather than
reinvented.

Export file format is undecided upstream (`docs/06-api-contracts.md`
§7's open item — not this milestone's decision, same standing as
TBD-006 for the bank transfer file). Generated as plain JSON here, a
clearly-labelled placeholder shape rather than a real CSV/XLSX/PDF
export — swapping the format later is a change to this task alone."""
import logging

from celery import shared_task
from django.utils import timezone

from audit.models import AuditLog
from audit.services import record

from .models import ReportExport
from .permissions import payroll_report_scope, report_scope
from .services import REPORT_BUILDERS
from .storage import generate_export_object_key, save_export_file

logger = logging.getLogger('reports')

PAYROLL_REPORT_TYPES = [ReportExport.REPORT_PAYROLL_COST, ReportExport.REPORT_PAYROLL_SUMMARY]
ORG_REPORT_TYPES = [ReportExport.REPORT_HEADCOUNT, ReportExport.REPORT_LEAVE_UTILIZATION, ReportExport.REPORT_TURNOVER]


def run_report_export(report_export):
    """Idempotent: re-running against the same row recomputes and
    overwrites, landing on the same result, same as
    `payroll.services.calculate_run`'s own idempotency note."""
    if report_export.report_type in PAYROLL_REPORT_TYPES:
        scope = payroll_report_scope(report_export.requested_by) or 'aggregate'
        data = REPORT_BUILDERS[report_export.report_type](scope, **report_export.params)
    else:
        scope = report_scope(report_export.requested_by) or 'aggregate'
        data = REPORT_BUILDERS[report_export.report_type](scope, report_export.requested_by, **report_export.params)

    object_key = generate_export_object_key(report_export.pk, report_export.report_type)
    save_export_file(object_key, data)
    report_export.object_key = object_key
    report_export.status = ReportExport.STATUS_COMPLETE
    report_export.generated_at = timezone.now()
    report_export.save(update_fields=['object_key', 'status', 'generated_at'])

    if report_export.report_type == ReportExport.REPORT_PAYROLL_COST:
        # `docs/06-api-contracts.md` §4.15's own note: an export touching
        # payroll cost emits an audit entry; the other four report types
        # do not.
        record(
            actor=report_export.requested_by,
            category=AuditLog.CATEGORY_PAYROLL_ACTION,
            action='report_export.payroll_cost',
            target_type='report_export',
            target_id=report_export.pk,
        )


@shared_task(bind=True, max_retries=2)
def run_report_export_task(self, report_export_id):
    report_export = ReportExport.objects.get(pk=report_export_id)
    try:
        run_report_export(report_export)
    except Exception:
        report_export.status = ReportExport.STATUS_FAILED
        report_export.failed_reason = 'report export failed'
        report_export.save(update_fields=['status', 'failed_reason'])
        logger.exception('report export failed for job %s', report_export_id)
        raise
