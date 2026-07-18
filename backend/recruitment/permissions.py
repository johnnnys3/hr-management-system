from rest_framework.permissions import SAFE_METHODS, BasePermission

from iam.roles import HR_ADMINISTRATOR, RECRUITER


class CanAccessJobRequisitions(BasePermission):
    """`docs/06-api-contracts.md` §4.6 / `docs/07-iam-rbac.md` §4.2's
    Recruitment row: Recruiter holds C, R, U; HR Administrator holds R."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return user.groups.filter(name__in=[RECRUITER, HR_ADMINISTRATOR]).exists()
        return user.groups.filter(name=RECRUITER).exists()


class CanDecideRequisition(BasePermission):
    """`/api/job-requisitions/{id}/approve/` and `/reject/`:
    `docs/07-iam-rbac.md` §4.2's "Requisition approval" row — HR
    Administrator only."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.groups.filter(name=HR_ADMINISTRATOR).exists())


class IsRecruiter(BasePermission):
    """Recruiter-only surface: job postings, candidates, applications,
    interviews, and offers all read `docs/06-api-contracts.md` §4.6 as
    "Recruiter" only, with no other role granted any access."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.groups.filter(name=RECRUITER).exists())
