from django.contrib.auth.models import Group
from rest_framework import serializers

from accounts.models import User

from .models import RoleGrantRequest
from .roles import ASSIGNED_ROLES


class UserAdminSerializer(serializers.ModelSerializer):
    """`/api/users/`, `docs/06-api-contracts.md` §4.9. `is_superuser` and
    `is_staff` are deliberately absent from `fields` — §7.2 reserves
    `is_superuser` for the break-glass account, and this endpoint, reachable
    by every System Administrator, must not be a route to granting it.
    `groups` is read-only here: role assignment goes through
    `/api/role-grant-requests/`, which is where §7.3's self-grant and
    privileged-approval constraints are enforced. Exposing it writable here
    would be a second, unconstrained grant path.
    """

    password = serializers.CharField(write_only=True, required=False, trim_whitespace=False)
    groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = User
        fields = ['id', 'email', 'is_active', 'groups', 'password', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class RoleGrantRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleGrantRequest
        fields = ['id', 'requester', 'subject', 'role', 'status', 'approver', 'requested_at', 'decided_at']
        read_only_fields = fields


class RoleGrantRequestCreateSerializer(serializers.Serializer):
    subject_user_id = serializers.PrimaryKeyRelatedField(source='subject', queryset=User.objects.all())
    # Restricted to the six assigned-role groups (`docs/07-iam-rbac.md`
    # §2.3), not `Group.objects.all()` — an arbitrary existing Django group
    # unrelated to RBAC would otherwise be requestable and, for anything
    # outside `PRIVILEGED_ROLES`, granted immediately with no approval step.
    role_id = serializers.PrimaryKeyRelatedField(
        source='role', queryset=Group.objects.filter(name__in=ASSIGNED_ROLES),
    )


class RoleGrantRequestDecisionSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=[RoleGrantRequest.STATUS_APPROVED, RoleGrantRequest.STATUS_REFUSED])
