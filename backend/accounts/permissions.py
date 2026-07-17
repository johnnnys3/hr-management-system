from rest_framework.permissions import BasePermission


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
