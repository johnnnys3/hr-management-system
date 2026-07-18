from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'category', 'channel', 'subject', 'body', 'related_type', 'related_id', 'read_at', 'created_at',
        ]
        read_only_fields = fields
