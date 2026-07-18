from rest_framework import serializers

from employees.models import Employee

from .models import ReportingRelationship


class ReportingRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportingRelationship
        fields = ['id', 'employee', 'manager_employee', 'effective_from']
        read_only_fields = ['id']

    def validate(self, attrs):
        employee = attrs.get('employee', getattr(self.instance, 'employee', None))
        manager_employee = attrs.get('manager_employee', getattr(self.instance, 'manager_employee', None))
        if employee is not None and manager_employee is not None and employee.pk == manager_employee.pk:
            raise serializers.ValidationError('an employee cannot be their own manager.')
        return attrs


class ManagerChangeSerializer(serializers.Serializer):
    manager_employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())

    def validate(self, attrs):
        if self.context['employee'].pk == attrs['manager_employee_id'].pk:
            raise serializers.ValidationError('an employee cannot be their own manager.')
        return attrs
