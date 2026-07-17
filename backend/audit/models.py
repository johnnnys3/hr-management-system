from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """The audit log, SRS §6.1. `docs/05-database-schema.md` §3.1 is the design this mirrors.

    No `updated_at`, no delete path: immutability is a PostgreSQL grant
    (`docs/07-iam-rbac.md` §7.3), not a Django-layer mechanism, and nothing
    here is designed to be mutated after insert.
    """

    CATEGORY_LOGIN_ATTEMPT = 'login_attempt'
    CATEGORY_RECORD_CHANGE = 'record_change'
    CATEGORY_PAYROLL_ACTION = 'payroll_action'
    CATEGORY_APPROVAL = 'approval'
    CATEGORY_PERMISSION_CHANGE = 'permission_change'
    CATEGORY_SECOND_FACTOR_EVENT = 'second_factor_event'
    CATEGORY_CHOICES = [
        (CATEGORY_LOGIN_ATTEMPT, 'Login attempt'),
        (CATEGORY_RECORD_CHANGE, 'Record change'),
        (CATEGORY_PAYROLL_ACTION, 'Payroll action'),
        (CATEGORY_APPROVAL, 'Approval'),
        (CATEGORY_PERMISSION_CHANGE, 'Permission change'),
        (CATEGORY_SECOND_FACTOR_EVENT, 'Second-factor event'),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
        db_column='actor_user_id',
        help_text='Null for pre-authentication events (a failed login against a non-existent account).',
    )
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    target_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='The model the event concerns, e.g. "employee"; null for events with no single target.',
    )
    target_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text='Not a foreign key — the audit log must outlive the row it describes.',
    )
    action = models.CharField(max_length=100, help_text='e.g. create, update, approve, refuse, login_success, login_failed.')
    detail = models.JSONField(null=True, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_log'
        ordering = ['-occurred_at']

    def __str__(self):
        return f'{self.category}:{self.action}@{self.occurred_at.isoformat()}'
