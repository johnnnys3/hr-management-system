from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models


class RoleGrantRequest(models.Model):
    """`role_grant_request`, `docs/05-database-schema.md` §4.3. Mechanism
    for `docs/07-iam-rbac.md` §7.3 and ADR-0010: self-grant refused,
    privileged grant needs an approver who is not the requester. Both are
    identity comparisons and both are database `CHECK` constraints, not
    just application code — `docs/06-api-contracts.md` §4.9 treats the API
    layer as defence in depth over the constraint, not the enforcement.
    """

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REFUSED = 'refused'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REFUSED, 'Refused'),
    ]

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name='role_grant_requests_made',
    )
    subject = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name='role_grant_requests_received',
        help_text='The user the role would be granted to.',
    )
    role = models.ForeignKey(Group, on_delete=models.RESTRICT, related_name='+')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name='+',
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'role_grant_request'
        permissions = [
            ('approve_role_grant', 'Can approve or refuse a privileged role-grant request'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(requester=models.F('subject')),
                name='role_grant_request_no_self_grant',
            ),
            models.CheckConstraint(
                condition=models.Q(approver__isnull=True) | ~models.Q(approver=models.F('requester')),
                name='role_grant_request_approver_not_requester',
            ),
        ]

    def __str__(self):
        return f'role grant request {self.role_id} for user {self.subject_id} ({self.status})'
