from rest_framework import serializers

from .models import (
    AllowanceType,
    Benefit,
    BenefitEnrollment,
    BonusAward,
    BonusCycle,
    CompensationRecord,
    EmployeeAllowance,
    PayGrade,
    SalaryStructure,
)


class SalaryStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryStructure
        fields = ['id', 'name', 'description', 'effective_from', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PayGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayGrade
        fields = ['id', 'salary_structure', 'name', 'min_salary', 'max_salary', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        min_salary = attrs.get('min_salary', getattr(self.instance, 'min_salary', None))
        max_salary = attrs.get('max_salary', getattr(self.instance, 'max_salary', None))
        if min_salary is not None and max_salary is not None and max_salary < min_salary:
            raise serializers.ValidationError({'max_salary': 'max_salary cannot be less than min_salary.'})
        return attrs


class PayGradeOptionSerializer(serializers.ModelSerializer):
    """Blind-selection view of a pay grade for roles without compensation
    access (Recruiter) — id, name, and the parent salary structure's name
    (not the structure's other fields), no salary figures. The structure
    name disambiguates pay grades that share a name across different
    structures (issue #107) — `PayGrade.name` is not unique organisation-wide,
    only within a `salary_structure`."""

    salary_structure_name = serializers.CharField(source='salary_structure.name', read_only=True)

    class Meta:
        model = PayGrade
        fields = ['id', 'name', 'salary_structure_name']


class CompensationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompensationRecord
        fields = [
            'id', 'employee', 'pay_grade', 'base_salary', 'currency',
            'effective_from', 'effective_to', 'is_superseded', 'recorded_by', 'created_at',
        ]
        read_only_fields = ['id', 'effective_to', 'is_superseded', 'recorded_by', 'created_at']


class CompensationRecordCreateSerializer(serializers.ModelSerializer):
    """`POST /api/employees/{id}/compensation-records/`,
    `docs/06-api-contracts.md` §4.13. `employee` and `recorded_by` are
    fixed by the view, not client-supplied. No PATCH/DELETE exists on
    this endpoint — a correction is a new POST with a later
    `effective_from`, superseding the prior current row server-side."""

    class Meta:
        model = CompensationRecord
        fields = ['id', 'pay_grade', 'base_salary', 'currency', 'effective_from']
        read_only_fields = ['id']


class BonusCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BonusCycle
        fields = ['id', 'name', 'period_start', 'period_end', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BonusAwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BonusAward
        fields = ['id', 'bonus_cycle', 'employee', 'amount', 'awarded_at']
        read_only_fields = ['id', 'bonus_cycle', 'awarded_at']


class AllowanceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllowanceType
        fields = [
            'id', 'name', 'calculation_method', 'amount_or_rate', 'is_taxable', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        calculation_method = attrs.get('calculation_method', getattr(self.instance, 'calculation_method', None))
        amount_or_rate = attrs.get('amount_or_rate', getattr(self.instance, 'amount_or_rate', None))
        if calculation_method == AllowanceType.CALCULATION_PERCENTAGE and amount_or_rate is not None and amount_or_rate > 1:
            raise serializers.ValidationError(
                {'amount_or_rate': 'a percentage_of_salary rate must be a fraction between 0 and 1.'}
            )
        return attrs


class EmployeeAllowanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAllowance
        fields = [
            'id', 'employee', 'allowance_type', 'amount_override',
            'effective_from', 'effective_to', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeAllowanceCreateSerializer(serializers.ModelSerializer):
    """`POST /api/employees/{id}/allowances/`, `docs/06-api-contracts.md`
    §4.13. `employee` is fixed by the view, not client-supplied."""

    class Meta:
        model = EmployeeAllowance
        fields = ['id', 'allowance_type', 'amount_override', 'effective_from', 'effective_to']
        read_only_fields = ['id']


class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = ['id', 'name', 'provider', 'cost', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BenefitEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BenefitEnrollment
        fields = ['id', 'employee', 'benefit', 'status', 'enrolled_at', 'cancelled_at']
        read_only_fields = ['id', 'enrolled_at', 'cancelled_at']


class BenefitEnrollmentCreateSerializer(serializers.ModelSerializer):
    """`POST /api/employees/{id}/benefit-enrollments/`. `employee` is
    fixed by the view, not client-supplied."""

    class Meta:
        model = BenefitEnrollment
        fields = ['id', 'benefit']
        read_only_fields = ['id']


class BenefitEnrollmentUpdateSerializer(serializers.ModelSerializer):
    """`PATCH /api/employees/{id}/benefit-enrollments/{id}/`.
    `{"status": "cancelled"}` is the only transition this endpoint
    accepts; the view sets `cancelled_at` when it happens."""

    class Meta:
        model = BenefitEnrollment
        fields = ['id', 'status']
        read_only_fields = ['id']

    def validate_status(self, value):
        if value != BenefitEnrollment.STATUS_CANCELLED:
            raise serializers.ValidationError('this endpoint only accepts status=cancelled.')
        return value
