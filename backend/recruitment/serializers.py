from rest_framework import serializers

from .models import Candidate, CandidateApplication, Interview, JobPosting, JobRequisition, OfferLetter


def _validate_offered_salary(value):
    if value < 0:
        raise serializers.ValidationError('offered_salary must not be negative.')


class JobRequisitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRequisition
        fields = [
            'id', 'department', 'job_title', 'requested_by', 'status', 'approved_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'requested_by', 'status', 'approved_by', 'created_at', 'updated_at']


class JobPostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = [
            'id', 'requisition', 'title', 'description', 'channel', 'published_at', 'closed_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'published_at', 'closed_at', 'created_at', 'updated_at']


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'resume_object_key', 'created_at']
        read_only_fields = ['id', 'resume_object_key', 'created_at']


class CandidateApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateApplication
        fields = ['id', 'candidate', 'posting', 'stage', 'applied_at', 'updated_at']
        read_only_fields = ['id', 'candidate', 'stage', 'applied_at', 'updated_at']


class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = [
            'id', 'application', 'interviewer_employee', 'scheduled_at', 'status', 'feedback',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'application', 'created_at', 'updated_at']


class OfferLetterSerializer(serializers.ModelSerializer):
    offered_salary = serializers.DecimalField(max_digits=14, decimal_places=2, validators=[_validate_offered_salary])

    class Meta:
        model = OfferLetter
        fields = [
            'id', 'application', 'offered_salary', 'status', 'issued_at', 'decided_at', 'document_object_key',
        ]
        read_only_fields = ['id', 'application', 'status', 'issued_at', 'decided_at', 'document_object_key']


class OfferDecisionSerializer(serializers.Serializer):
    DECISION_CHOICES = [OfferLetter.STATUS_ACCEPTED, OfferLetter.STATUS_REJECTED, OfferLetter.STATUS_WITHDRAWN]

    decision = serializers.ChoiceField(choices=DECISION_CHOICES)
