from datetime import date

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

import audit.services
from audit.models import AuditLog
from employees.models import Employee, EmploymentHistory
from employees.serializers import EmployeeSerializer

from .models import ReportingRelationship
from .permissions import CanAccessDirectReports, CanAccessReportingRelationships, CanChangeManager
from .serializers import ManagerChangeSerializer, ReportingRelationshipSerializer


class ReportingRelationshipListView(APIView):
    """`GET /api/reporting-relationships/`, `docs/06-api-contracts.md`
    §4.5. Filterable by `manager_employee_id`."""

    permission_classes = [CanAccessReportingRelationships]

    def get(self, request):
        queryset = ReportingRelationship.objects.order_by('employee_id')
        manager_employee_id = request.query_params.get('manager_employee_id')
        if manager_employee_id:
            queryset = queryset.filter(manager_employee_id=manager_employee_id)
        return Response(ReportingRelationshipSerializer(queryset, many=True).data)


class DirectReportsView(APIView):
    """`GET /api/employees/{id}/direct-reports/`, `docs/06-api-contracts.md`
    §4.5. The query is `docs/05-database-schema.md` §4.6's derivation query,
    not a separate index — direct reports only, no transitive chain
    (`docs/07-iam-rbac.md` §5)."""

    permission_classes = [CanAccessDirectReports]

    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        self.check_object_permissions(request, employee)
        reports = Employee.objects.filter(
            pk__in=ReportingRelationship.objects.filter(manager_employee_id=employee.pk).values('employee_id')
        ).order_by('employee_number')
        return Response(EmployeeSerializer(reports, many=True).data)


class ManagerChangeView(APIView):
    """`PATCH /api/employees/{id}/manager/`, `docs/06-api-contracts.md`
    §4.5. Writes/replaces the current-state `reporting_relationship` row
    (`docs/05-database-schema.md` §4.6 — one row per employee, not a new
    row per change) and an `employment_history` row recording the change."""

    permission_classes = [CanChangeManager]

    def patch(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = ManagerChangeSerializer(data=request.data, context={'employee': employee})
        serializer.is_valid(raise_exception=True)
        new_manager = serializer.validated_data['manager_employee_id']

        with transaction.atomic():
            previous_manager_id = getattr(
                ReportingRelationship.objects.select_for_update().filter(employee=employee).first(),
                'manager_employee_id',
                None,
            )
            relationship, _ = ReportingRelationship.objects.update_or_create(
                employee=employee,
                defaults={'manager_employee': new_manager, 'effective_from': date.today()},
            )
            EmploymentHistory.objects.create(
                employee=employee,
                event_type=EmploymentHistory.EVENT_MANAGER_CHANGE,
                effective_date=date.today(),
                previous_value={'manager_employee_id': previous_manager_id},
                new_value={'manager_employee_id': new_manager.pk},
                recorded_by=request.user,
            )
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='employee_manager_changed',
                actor=request.user,
                target_type='employee',
                target_id=employee.pk,
            )
        return Response(ReportingRelationshipSerializer(relationship).data)
