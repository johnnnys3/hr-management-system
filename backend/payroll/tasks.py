"""Celery tasks for the two async payroll actions, `docs/06-api-
contracts.md` §4.14: `calculate/` and `finalize/` return `202` and the
caller polls `GET /payroll-runs/{id}/` for `status`. Both wrap an
idempotent service function (HRMS-NFR-005) — a retried task re-runs the
same computation and lands on the same result rather than duplicating
work, per `services.calculate_run`/`services.finalize_run`'s own
docstrings."""
import logging

from celery import shared_task

from .models import PayrollRun
from .services import calculate_run, finalize_run

logger = logging.getLogger('payroll')


@shared_task(bind=True, max_retries=2)
def calculate_run_task(self, payroll_run_id):
    payroll_run = PayrollRun.objects.get(pk=payroll_run_id)
    try:
        calculate_run(payroll_run)
    except Exception:
        payroll_run.status = PayrollRun.STATUS_FAILED
        payroll_run.save(update_fields=['status'])
        logger.exception('payroll calculate failed for run %s', payroll_run_id)
        raise


@shared_task(bind=True, max_retries=2)
def finalize_run_task(self, payroll_run_id):
    payroll_run = PayrollRun.objects.get(pk=payroll_run_id)
    try:
        finalize_run(payroll_run)
    except Exception:
        payroll_run.status = PayrollRun.STATUS_FAILED
        payroll_run.save(update_fields=['status'])
        logger.exception('payroll finalize failed for run %s', payroll_run_id)
        raise
