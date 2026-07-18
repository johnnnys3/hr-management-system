from rest_framework import serializers

from employees.models import Employee

from .models import ReportingRelationship


class ReportingRelationshipSerializer(serializers.ModelSerializer):
    """Read-only: every write to `reporting_relationship` goes through
    `ManagerChangeSerializer` and `ManagerChangeView`'s `update_or_create`,
    not this serializer."""

    class Meta:
        model = ReportingRelationship
        fields = ('id', 'employee', 'manager_employee', 'effective_from')
        read_only_fields = fields


class ManagerChangeSerializer(serializers.Serializer):
    manager_employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())

    def validate(self, attrs):
        if self.context['employee'].pk == attrs['manager_employee_id'].pk:
            raise serializers.ValidationError('an employee cannot be their own manager.')
        return attrs
