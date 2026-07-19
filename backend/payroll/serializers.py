from rest_framework import serializers

from .models import BankTransferFile, PayrollRun, Payslip, PayslipLine, StatutoryRateTable


class StatutoryRateTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatutoryRateTable
        fields = ['id', 'rate_type', 'effective_from', 'effective_to', 'rates', 'created_at']
        read_only_fields = fields


class PayrollRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollRun
        fields = [
            'id', 'period_start', 'period_end', 'status', 'initiated_by',
            'approved_by', 'approved_at', 'finalized_at', 'created_at',
        ]
        read_only_fields = ['id', 'status', 'initiated_by', 'approved_by', 'approved_at', 'finalized_at', 'created_at']


class PayrollRunCreateSerializer(serializers.ModelSerializer):
    """`POST /api/payroll-runs/`, `docs/06-api-contracts.md` §4.14.
    `initiated_by` is fixed by the view, not client-supplied. The
    `(period_start, period_end)` uniqueness is checked by the view, not
    left to `ModelSerializer`'s auto-generated `UniqueTogetherValidator`
    — the contract asks for `409 conflict` on a duplicate period, not
    the validator's `400`."""

    class Meta:
        model = PayrollRun
        fields = ['id', 'period_start', 'period_end']
        read_only_fields = ['id']
        validators = []

    def validate(self, attrs):
        if attrs['period_end'] < attrs['period_start']:
            raise serializers.ValidationError({'period_end': 'period_end cannot be earlier than period_start.'})
        return attrs


class PayslipLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayslipLine
        fields = ['id', 'line_type', 'source_type', 'source_id', 'description', 'amount', 'created_at']
        read_only_fields = fields


class PayslipSerializer(serializers.ModelSerializer):
    lines = PayslipLineSerializer(many=True, read_only=True)

    class Meta:
        model = Payslip
        fields = [
            'id', 'payroll_run', 'employee', 'gross_pay', 'net_pay', 'currency', 'generated_at', 'lines',
            'object_key',
        ]
        read_only_fields = fields


class BankTransferFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankTransferFile
        fields = ['id', 'payroll_run', 'object_key', 'generated_at']
        read_only_fields = fields
