from rest_framework import serializers

from .models import SecondFactorRecoveryRequest, User


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)
    totp_code = serializers.CharField(required=False, allow_blank=True)


class MeSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = User
        fields = ['id', 'email', 'groups']


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False)


class SecondFactorEnrollResponseSerializer(serializers.Serializer):
    provisioning_uri = serializers.CharField()


class SecondFactorRecoveryRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondFactorRecoveryRequest
        fields = ['id', 'status', 'requested_at', 'decided_at']
        read_only_fields = fields


class SecondFactorRecoveryDecisionSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=['approved', 'denied'])
