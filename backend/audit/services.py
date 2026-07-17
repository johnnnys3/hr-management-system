"""The one append-only writer, per `docs/02-project-plan.md` §7.3.

Emission — deciding which of a module's own events to record — is each
consumer's job, absorbed into that module's own estimate (CONTEXT.md,
"Emission"). This function is the only thing that writes to `audit_log`.
"""
from .models import AuditLog


def record(*, category, action, actor=None, target_type=None, target_id=None, detail=None):
    return AuditLog.objects.create(
        actor=actor,
        category=category,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
    )
