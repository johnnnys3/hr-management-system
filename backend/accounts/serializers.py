from rest_framework import serializers

from iam.roles import is_employee, is_manager

from .models import SecondFactorRecoveryRequest, User


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)
    totp_code = serializers.CharField(required=False, allow_blank=True)


class MeSerializer(serializers.ModelSerializer):
    """`docs/06-api-contracts.md` §4.2's `/api/auth/me/` row promises "the
    caller's ... derived role set (Employee/Manager, `docs/07-iam-rbac.md`
    §3)" alongside assigned groups — `is_employee`/`is_manager` close that
    gap (found unimplemented via a client-side consequence: no frontend
    module could route-gate Manager-specific UI, since nothing on this
    endpoint said whether the caller held the role)."""

    groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    is_employee = serializers.SerializerMethodField()
    is_manager = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'groups', 'is_employee', 'is_manager', 'phone_verified_at']

    def get_is_employee(self, user):
        return is_employee(user)

    def get_is_manager(self, user):
        return is_manager(user)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False)


class PhoneVerificationRequestSerializer(serializers.Serializer):
    phone_number = serializers.RegexField(regex=r'\A\+[1-9][0-9]{6,14}\Z')


class PhoneVerificationConfirmSerializer(serializers.Serializer):
    code = serializers.RegexField(regex=r'\A[0-9]{6}\Z')


class SecondFactorEnrollResponseSerializer(serializers.Serializer):
    provisioning_uri = serializers.CharField()


class SecondFactorRecoveryRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondFactorRecoveryRequest
        fields = ['id', 'status', 'requested_at', 'decided_at']
        read_only_fields = fields


class SecondFactorRecoveryDecisionSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=['approved', 'denied'])
