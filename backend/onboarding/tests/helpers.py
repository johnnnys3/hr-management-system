from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


def user_with_role(email, role_name):
    user = User.objects.create_user(email=email, password='x')
    user.groups.add(Group.objects.get(name=role_name))
    return user
