from rest_framework.permissions import SAFE_METHODS, BasePermission

from iam.roles import HR_ADMINISTRATOR, HR_OFFICER


class CanConvert(BasePermission):
    """`docs/07-iam-rbac.md` §4.2's Onboarding row: HR Officer holds C on the
    conversion endpoint only.
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.groups.filter(name=HR_OFFICER).exists())


class CanAccessOnboarding(BasePermission):
    """`docs/07-iam-rbac.md` §4.2's Onboarding row: HR Officer holds C, R, U;
    HR Administrator holds R (absorbed from Recruiter, retired — ADR-0013).
    """

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return user.groups.filter(name__in=[HR_OFFICER, HR_ADMINISTRATOR]).exists()
        return user.groups.filter(name=HR_OFFICER).exists()
