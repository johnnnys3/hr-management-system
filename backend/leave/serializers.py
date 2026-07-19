from rest_framework import serializers

from .models import LeaveBalance, LeaveRequest, LeaveType


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ['id', 'name', 'requires_approval', 'is_active', 'created_at', 'updated_at']
        read_only_fields = fields


class LeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = [
            'id', 'employee', 'leave_type', 'period_start', 'period_end',
            'entitled_days', 'used_days', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'used_days', 'created_at', 'updated_at']


class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'leave_type', 'start_date', 'end_date', 'reason',
            'status', 'approved_by', 'decided_at', 'created_at',
        ]
        read_only_fields = ['id', 'status', 'approved_by', 'decided_at', 'created_at']


class LeaveRequestCreateSerializer(serializers.ModelSerializer):
    """`POST /api/leave-requests/`, `docs/06-api-contracts.md` §4.12.
    `employee` is fixed to the caller in the view, not client-supplied."""

    class Meta:
        model = LeaveRequest
        fields = ['id', 'leave_type', 'start_date', 'end_date', 'reason']
        read_only_fields = ['id']

    def validate(self, attrs):
        if attrs['end_date'] < attrs['start_date']:
            raise serializers.ValidationError({'end_date': 'end_date cannot be earlier than start_date.'})
        return attrs


class LeaveRequestCorrectionSerializer(serializers.ModelSerializer):
    """`PATCH /api/leave-requests/{id}/`, `docs/06-api-contracts.md` §4.12.
    HR Officer correction/cancellation only — `status` cannot be set to
    `'approved'` or `'rejected'` here; both transitions are Manager-only
    actions (`approve/`, `reject/`), so the same field is never reachable
    by two permission paths."""

    class Meta:
        model = LeaveRequest
        fields = ['id', 'leave_type', 'start_date', 'end_date', 'reason', 'status']
        read_only_fields = ['id']

    def validate_status(self, value):
        if value in (LeaveRequest.STATUS_APPROVED, LeaveRequest.STATUS_REJECTED):
            raise serializers.ValidationError(
                'HR Officer cannot approve or reject a leave request through this endpoint.'
            )
        return value

    def validate(self, attrs):
        start_date = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({'end_date': 'end_date cannot be earlier than start_date.'})
        return attrs
