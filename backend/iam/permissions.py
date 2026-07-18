from rest_framework.permissions import BasePermission

from accounts.permissions import IsFullyAuthenticated  # noqa: F401  (re-exported for iam.views)
from audit.permissions import IsSystemAdministrator  # noqa: F401  (re-exported for iam.views)

# `audit.permissions.IsSystemAdministrator` (module 1) already implements
# this exact check — group membership, deliberately `has_perm`-free per
# §7.2's `is_superuser` prohibition. `/api/users/` reuses it rather than
# defining a second, identical class.


class CanDecideRoleGrantRequest(BasePermission):
    """`docs/07-iam-rbac.md` §7.3: a privileged grant is decided only by an
    `iam.approve_role_grant` holder who is not the requester. Defence in
    depth over the `role_grant_request_approver_not_requester` database
    constraint — the constraint is the actual enforcement.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.pk == obj.requester_id:
            return False
        if user.is_superuser:
            # `docs/07-iam-rbac.md` §7.2: `is_superuser` is reserved for
            # break-glass, and `has_perm` short-circuits to `True` for it
            # regardless of held permissions. Falling through to that call
            # would make the break-glass account an unconditional approver
            # of every privileged grant, which §7.3's whole point is to
            # prevent for the System Administrator role it stands in for.
            return False
        return user.has_perm('iam.approve_role_grant')
