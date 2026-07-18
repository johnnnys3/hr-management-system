from rest_framework.permissions import SAFE_METHODS, BasePermission

from iam.roles import HR_ADMINISTRATOR, HR_OFFICER, PAYROLL_OFFICER, RECRUITER

READ_ROLES = [HR_ADMINISTRATOR, HR_OFFICER, RECRUITER, PAYROLL_OFFICER]


class CanAccessHRConfiguration(BasePermission):
    """`docs/07-iam-rbac.md` §4.2's HR configuration row: HR Administrator
    holds C, R, U; HR Officer, Recruiter, and Payroll Officer hold R only.
    """

    def has_permission(self, request, view):
        """Determine whether a user may access the requested HR configuration operation.
        
        Parameters:
            request: The request whose user and HTTP method determine access.
            view: The view associated with the request.
        
        Returns:
            bool: `True` if the authenticated user has the required HR role for the operation, `False` otherwise.
        """
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return user.groups.filter(name__in=READ_ROLES).exists()
        return user.groups.filter(name=HR_ADMINISTRATOR).exists()
