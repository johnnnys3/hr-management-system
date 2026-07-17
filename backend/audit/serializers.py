from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ['id', 'actor', 'category', 'target_type', 'target_id', 'action', 'detail', 'occurred_at']
        read_only_fields = fields
