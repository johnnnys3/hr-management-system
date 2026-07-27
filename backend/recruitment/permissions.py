from rest_framework.permissions import SAFE_METHODS, BasePermission

from iam.roles import HR_ADMINISTRATOR, HR_OFFICER


class CanAccessJobRequisitions(BasePermission):
    """`docs/06-api-contracts.md` §4.6 / `docs/07-iam-rbac.md` §4.2's
    Recruitment row: HR Administrator holds C, R, U (absorbed from
    Recruiter, retired — ADR-0013)."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.groups.filter(name=HR_ADMINISTRATOR).exists())


class CanDecideRequisition(BasePermission):
    """`/api/job-requisitions/{id}/approve/` and `/reject/`:
    `docs/07-iam-rbac.md` §4.2's "Requisition approval" row — HR
    Administrator only. The approver-not-requester check is enforced in
    the view and at the database layer (`job_requisition_approver_not_requester`),
    not here — this class only gates who may attempt a decision at all."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.groups.filter(name=HR_ADMINISTRATOR).exists())


class CanWriteRecruitment(BasePermission):
    """Job postings, candidates, applications, interviews, and offers:
    HR Administrator holds full C/R/U access (absorbed from Recruiter,
    retired — ADR-0013); HR Officer holds R only, per
    `docs/07-iam-rbac.md` §4.2's Recruitment row (HR Officer needs to reach
    an accepted offer to trigger HRMS-BR-013 conversion, module 9)."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return user.groups.filter(name__in=[HR_ADMINISTRATOR, HR_OFFICER]).exists()
        return user.groups.filter(name=HR_ADMINISTRATOR).exists()
