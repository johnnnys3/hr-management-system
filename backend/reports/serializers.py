from rest_framework import serializers

from .models import ReportExport
from .storage import signed_download_url


class ReportExportCreateSerializer(serializers.Serializer):
    params = serializers.JSONField(required=False, default=dict)


class ReportExportSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = ReportExport
        fields = [
            'id', 'report_type', 'params', 'status', 'download_url', 'failed_reason', 'generated_at', 'created_at',
        ]
        read_only_fields = fields

    def get_download_url(self, obj):
        if obj.status != ReportExport.STATUS_COMPLETE or not obj.object_key:
            return None
        return signed_download_url(obj.object_key)
