from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from leave.tests.helpers import make_employee, make_manager_and_report  # noqa: F401 (re-exported for dashboard tests)

User = get_user_model()


def user_with_role(email, role_name=None, employee=None):
    """Like `leave.tests.helpers.user_with_role`, but `role_name` is
    optional: dashboard tests need users with an employee record and no
    assigned role at all (a plain Employee), which that helper doesn't
    support since every leave-app test user has one."""
    user = User.objects.create_user(email=email, password='x', employee=employee)
    if role_name:
        user.groups.add(Group.objects.get(name=role_name))
    return user
