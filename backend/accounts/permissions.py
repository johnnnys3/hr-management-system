from rest_framework.permissions import BasePermission, IsAuthenticated

SECOND_FACTOR_ENROLLMENT_PENDING_SESSION_KEY = 'second_factor_enrollment_pending'


class IsFullyAuthenticated(IsAuthenticated):
    """A session established for an account required to enrol a second
    factor but which hasn't yet (`LoginView`'s
    `second_factor_enrollment_required` path) is authenticated but not
    fully so: it may reach enrolment and logout, nothing else. This is the
    permission everything but those two endpoints uses.
    """

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return not request.session.get(SECOND_FACTOR_ENROLLMENT_PENDING_SESSION_KEY, False)


class CanDecideSecondFactorRecovery(BasePermission):
    """`docs/07-iam-rbac.md` §7.3/§8: the recovery approver holder is a
    deployment-time designation, granted the `accounts.decide_recovery_request`
    permission by whichever role the organisation designates — never to the
    requester themselves, and never (per the same section) to a System
    Administrator by default. This class checks the permission and the
    identity constraint; the "does not administer credentials" property is
    a role/permission-grant decision made at deployment (RBAC/IAM, module 4),
    not something this module can verify from data it owns.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.pk == obj.user_id:
            return False
        return user.has_perm('accounts.decide_recovery_request')
