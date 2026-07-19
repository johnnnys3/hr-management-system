from django.db import IntegrityError, transaction
from django.test import TestCase

from iam.roles import HR_OFFICER

from ..models import ReportExport
from .helpers import user_with_role


class ReportExportConstraintTests(TestCase):
    """CodeRabbit caught the first draft's constraints being satisfied
    trivially by `status='complete'` alone, regardless of whether
    `object_key`/`generated_at` were actually set — these prove the
    corrected implication direction."""

    def setUp(self):
        self.user = user_with_role('hr@example.com', HR_OFFICER)

    def test_complete_without_object_key_is_rejected(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            ReportExport.objects.create(
                report_type=ReportExport.REPORT_HEADCOUNT, requested_by=self.user,
                status=ReportExport.STATUS_COMPLETE, object_key=None, generated_at=None,
            )

    def test_pending_with_object_key_is_rejected(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            ReportExport.objects.create(
                report_type=ReportExport.REPORT_HEADCOUNT, requested_by=self.user,
                status=ReportExport.STATUS_PENDING, object_key='reports/exports/headcount/1.json',
            )

    def test_failed_without_reason_is_rejected(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            ReportExport.objects.create(
                report_type=ReportExport.REPORT_HEADCOUNT, requested_by=self.user,
                status=ReportExport.STATUS_FAILED, failed_reason=None,
            )

    def test_complete_with_object_key_is_accepted(self):
        export = ReportExport.objects.create(
            report_type=ReportExport.REPORT_HEADCOUNT, requested_by=self.user,
            status=ReportExport.STATUS_COMPLETE, object_key='reports/exports/headcount/1.json',
            generated_at='2026-01-01T00:00:00Z',
        )
        self.assertIsNotNone(export.pk)
