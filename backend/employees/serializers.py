from datetime import date

from rest_framework import serializers

from .models import EmergencyContact, Employee, EmployeeDocument, EmploymentHistory


def _validate_date_of_birth(value):
    if value >= date.today():
        raise serializers.ValidationError('date_of_birth must be in the past.')


def _validate_hire_date(value):
    if value > date.today():
        raise serializers.ValidationError('hire_date must not be in the future.')


class EmployeeSerializer(serializers.ModelSerializer):
    """HR-facing serializer, `docs/06-api-contracts.md` §4.3. HR Officer
    holds full C, R, U (`docs/07-iam-rbac.md` §4.2), including
    `employment_status` on `PATCH`. At creation `employment_status` is not
    client-settable — HRMS-FR-027's creation note: it defaults `active`
    regardless of what the request body carries; the view enforces this by
    overriding the field on `save()`, not by making it read-only here,
    since HR Officer's own `PATCH` needs to reach the same field.
    """

    date_of_birth = serializers.DateField(validators=[_validate_date_of_birth])
    hire_date = serializers.DateField(validators=[_validate_hire_date])

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_number', 'first_name', 'last_name', 'date_of_birth',
            'department', 'job_title', 'employment_status', 'hire_date',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeStatusUpdateSerializer(serializers.ModelSerializer):
    """HR Administrator's narrower write surface, `docs/07-iam-rbac.md`
    §4.2's "R, U status" cell — `PATCH` here reaches `employment_status`
    only, not the rest of the record."""

    class Meta:
        model = Employee
        fields = ['id', 'employment_status']
        read_only_fields = ['id']


class EmployeeSelfServiceSerializer(serializers.ModelSerializer):
    """`/api/employees/me/`, HRMS-FR-025 to HRMS-FR-027. A distinct,
    narrower serializer from `EmployeeSerializer` — not the same one with a
    permission check bolted on — so salary, job title, department, status,
    manager, name, and date of birth stay non-writable regardless of future
    additions to the HR-facing serializer. Identity fields (name, DOB) are
    HR Officer's to correct (`/api/employees/{id}/`, already full CRUD),
    not the employee's own — owner decision 2026-07-27. Everything on this
    model is now read-only here; the endpoint's write side lives on
    (`/api/employees/{id}/emergency-contacts/`) instead."""

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_number', 'first_name', 'last_name', 'date_of_birth',
            'department', 'job_title', 'employment_status', 'hire_date',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def update(self, instance, validated_data):
        """No-op when all fields are read-only (validated_data will be empty).
        Prevents unnecessary save() calls and audit events."""
        if not validated_data:
            return instance
        return super().update(instance, validated_data)


class EmploymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmploymentHistory
        fields = ['id', 'employee', 'event_type', 'effective_date', 'previous_value', 'new_value', 'recorded_by', 'created_at']
        read_only_fields = fields


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDocument
        fields = ['id', 'employee', 'document_type', 'file_name', 'content_type', 'size_bytes', 'uploaded_by', 'created_at']
        read_only_fields = ['id', 'employee', 'content_type', 'size_bytes', 'uploaded_by', 'created_at']


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ['id', 'employee', 'name', 'relationship', 'phone', 'email', 'is_primary', 'created_at', 'updated_at']
        read_only_fields = ['id', 'employee', 'created_at', 'updated_at']
