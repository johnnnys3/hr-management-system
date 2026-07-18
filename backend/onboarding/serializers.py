from rest_framework import serializers

from recruitment.models import CandidateApplication

from .models import OnboardingChecklist, OnboardingTask


class OnboardingTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingTask
        fields = [
            'id', 'checklist', 'name', 'is_required', 'status', 'completed_by', 'completed_at', 'created_at',
        ]
        read_only_fields = ['id', 'checklist', 'status', 'completed_by', 'completed_at', 'created_at']


class OnboardingTaskStatusUpdateSerializer(serializers.ModelSerializer):
    """`PATCH {"status": "completed"}`, `docs/06-api-contracts.md` §4.7 — sets
    `completed_by`, `completed_at` as a side effect, not client-settable directly.
    """

    class Meta:
        model = OnboardingTask
        fields = ['status']


class OnboardingChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingChecklist
        fields = ['id', 'employee', 'application', 'started_at', 'completed_at']
        read_only_fields = fields


class ConvertFromApplicationSerializer(serializers.Serializer):
    application_id = serializers.PrimaryKeyRelatedField(queryset=CandidateApplication.objects.all())
    employee_number = serializers.CharField(max_length=64)
    date_of_birth = serializers.DateField()
    department = serializers.IntegerField()
    job_title = serializers.IntegerField()
    hire_date = serializers.DateField()


class ConvertDirectHireSerializer(serializers.Serializer):
    employee_number = serializers.CharField(max_length=64)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    date_of_birth = serializers.DateField()
    department = serializers.IntegerField()
    job_title = serializers.IntegerField()
    hire_date = serializers.DateField()
