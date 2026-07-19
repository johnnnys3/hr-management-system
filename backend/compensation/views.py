from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import audit.services
from audit.models import AuditLog
from employees.models import Employee

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
from .permissions import (
    CanAccessAllowanceTypes,
    CanAccessBenefitEnrollments,
    CanAccessBenefits,
    CanAccessBonusAwards,
    CanAccessBonusCycles,
    CanAccessCompensationRecords,
    CanAccessEmployeeAllowances,
    CanAccessSalaryFramework,
)
from .serializers import (
    AllowanceTypeSerializer,
    BenefitEnrollmentCreateSerializer,
    BenefitEnrollmentSerializer,
    BenefitEnrollmentUpdateSerializer,
    BenefitSerializer,
    BonusAwardSerializer,
    BonusCycleSerializer,
    CompensationRecordCreateSerializer,
    CompensationRecordSerializer,
    EmployeeAllowanceCreateSerializer,
    EmployeeAllowanceSerializer,
    PayGradeSerializer,
    SalaryStructureSerializer,
)


class SalaryStructureListCreateView(APIView):
    """`GET, POST /api/salary-structures/`, `docs/06-api-contracts.md` §4.13."""

    permission_classes = [CanAccessSalaryFramework]

    def get(self, request):
        return Response(SalaryStructureSerializer(SalaryStructure.objects.order_by('name'), many=True).data)

    def post(self, request):
        serializer = SalaryStructureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            salary_structure = serializer.save()
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='salary_structure_created',
                actor=request.user,
                target_type='salary_structure',
                target_id=salary_structure.pk,
            )
        return Response(SalaryStructureSerializer(salary_structure).data, status=status.HTTP_201_CREATED)


class SalaryStructureDetailView(APIView):
    """`PATCH /api/salary-structures/{id}/`."""

    permission_classes = [CanAccessSalaryFramework]

    def patch(self, request, pk):
        salary_structure = get_object_or_404(SalaryStructure, pk=pk)
        serializer = SalaryStructureSerializer(salary_structure, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            salary_structure = serializer.save()
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='salary_structure_updated',
                actor=request.user,
                target_type='salary_structure',
                target_id=salary_structure.pk,
            )
        return Response(SalaryStructureSerializer(salary_structure).data)


class PayGradeListCreateView(APIView):
    """`GET, POST /api/pay-grades/`, `docs/06-api-contracts.md` §4.13."""

    permission_classes = [CanAccessSalaryFramework]

    def get(self, request):
        return Response(PayGradeSerializer(PayGrade.objects.order_by('salary_structure_id', 'name'), many=True).data)

    def post(self, request):
        serializer = PayGradeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            pay_grade = serializer.save()
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='pay_grade_created',
                actor=request.user,
                target_type='pay_grade',
                target_id=pay_grade.pk,
            )
        return Response(PayGradeSerializer(pay_grade).data, status=status.HTTP_201_CREATED)


class PayGradeDetailView(APIView):
    """`PATCH /api/pay-grades/{id}/`."""

    permission_classes = [CanAccessSalaryFramework]

    def patch(self, request, pk):
        pay_grade = get_object_or_404(PayGrade, pk=pk)
        serializer = PayGradeSerializer(pay_grade, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            pay_grade = serializer.save()
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='pay_grade_updated',
                actor=request.user,
                target_type='pay_grade',
                target_id=pay_grade.pk,
            )
        return Response(PayGradeSerializer(pay_grade).data)


class CompensationRecordListCreateView(APIView):
    """`GET, POST /api/employees/{id}/compensation-records/`,
    `docs/06-api-contracts.md` §4.13. No PATCH/DELETE — a correction is a
    new POST with a later `effective_from`, which supersedes the prior
    current row (`is_superseded`, `effective_to`) server-side, in the
    same transaction, per HRMS-DR-010/schema §3.4."""

    permission_classes = [CanAccessCompensationRecords]

    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        records = employee.compensation_records.order_by('-effective_from')
        return Response(CompensationRecordSerializer(records, many=True).data)

    def post(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = CompensationRecordCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            prior_current = (
                CompensationRecord.objects
                .select_for_update()
                .filter(employee=employee, is_superseded=False)
                .order_by('-effective_from')
                .first()
            )
            if prior_current is not None and serializer.validated_data['effective_from'] <= prior_current.effective_from:
                return Response(
                    {'effective_from': 'must be later than the current compensation record\'s effective_from.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            record = serializer.save(employee=employee, recorded_by=request.user)
            if prior_current is not None and prior_current.pk != record.pk:
                prior_current.is_superseded = True
                prior_current.effective_to = record.effective_from
                prior_current.save(update_fields=['is_superseded', 'effective_to'])
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='compensation_record_created',
                actor=request.user,
                target_type='compensation_record',
                target_id=record.pk,
            )
        return Response(CompensationRecordSerializer(record).data, status=status.HTTP_201_CREATED)


class BonusCycleListCreateView(APIView):
    """`GET, POST /api/bonus-cycles/`, `docs/06-api-contracts.md` §4.13."""

    permission_classes = [CanAccessBonusCycles]

    def get(self, request):
        return Response(BonusCycleSerializer(BonusCycle.objects.order_by('-period_start'), many=True).data)

    def post(self, request):
        serializer = BonusCycleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            bonus_cycle = serializer.save()
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='bonus_cycle_created',
                actor=request.user,
                target_type='bonus_cycle',
                target_id=bonus_cycle.pk,
            )
        return Response(BonusCycleSerializer(bonus_cycle).data, status=status.HTTP_201_CREATED)


class BonusCycleDetailView(APIView):
    """`PATCH /api/bonus-cycles/{id}/`."""

    permission_classes = [CanAccessBonusCycles]

    def patch(self, request, pk):
        bonus_cycle = get_object_or_404(BonusCycle, pk=pk)
        serializer = BonusCycleSerializer(bonus_cycle, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            bonus_cycle = serializer.save()
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='bonus_cycle_updated',
                actor=request.user,
                target_type='bonus_cycle',
                target_id=bonus_cycle.pk,
            )
        return Response(BonusCycleSerializer(bonus_cycle).data)


class BonusAwardListCreateView(APIView):
    """`GET, POST /api/bonus-cycles/{id}/awards/`,
    `docs/06-api-contracts.md` §4.13."""

    permission_classes = [CanAccessBonusAwards]

    def get(self, request, pk):
        bonus_cycle = get_object_or_404(BonusCycle, pk=pk)
        awards = bonus_cycle.awards.order_by('-awarded_at')
        return Response(BonusAwardSerializer(awards, many=True).data)

    def post(self, request, pk):
        bonus_cycle = get_object_or_404(BonusCycle, pk=pk)
        serializer = BonusAwardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            award = serializer.save(bonus_cycle=bonus_cycle)
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='bonus_award_created',
                actor=request.user,
                target_type='bonus_award',
                target_id=award.pk,
            )
        return Response(BonusAwardSerializer(award).data, status=status.HTTP_201_CREATED)


class AllowanceTypeListCreateView(APIView):
    """`GET, POST /api/allowance-types/`, `docs/06-api-contracts.md` §4.13."""

    permission_classes = [CanAccessAllowanceTypes]

    def get(self, request):
        return Response(AllowanceTypeSerializer(AllowanceType.objects.order_by('name'), many=True).data)

    def post(self, request):
        serializer = AllowanceTypeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            allowance_type = serializer.save()
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='allowance_type_created',
                actor=request.user,
                target_type='allowance_type',
                target_id=allowance_type.pk,
            )
        return Response(AllowanceTypeSerializer(allowance_type).data, status=status.HTTP_201_CREATED)


class AllowanceTypeDetailView(APIView):
    """`PATCH /api/allowance-types/{id}/`."""

    permission_classes = [CanAccessAllowanceTypes]

    def patch(self, request, pk):
        allowance_type = get_object_or_404(AllowanceType, pk=pk)
        serializer = AllowanceTypeSerializer(allowance_type, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            allowance_type = serializer.save()
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='allowance_type_updated',
                actor=request.user,
                target_type='allowance_type',
                target_id=allowance_type.pk,
            )
        return Response(AllowanceTypeSerializer(allowance_type).data)


class EmployeeAllowanceListCreateView(APIView):
    """`GET, POST /api/employees/{id}/allowances/`,
    `docs/06-api-contracts.md` §4.13."""

    permission_classes = [CanAccessEmployeeAllowances]

    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        allowances = employee.allowances.order_by('-effective_from')
        return Response(EmployeeAllowanceSerializer(allowances, many=True).data)

    def post(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmployeeAllowanceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            allowance = serializer.save(employee=employee)
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='employee_allowance_created',
                actor=request.user,
                target_type='employee_allowance',
                target_id=allowance.pk,
            )
        return Response(EmployeeAllowanceSerializer(allowance).data, status=status.HTTP_201_CREATED)


class BenefitListCreateView(APIView):
    """`GET, POST /api/benefits/`, `docs/06-api-contracts.md` §4.13."""

    permission_classes = [CanAccessBenefits]

    def get(self, request):
        return Response(BenefitSerializer(Benefit.objects.order_by('name'), many=True).data)

    def post(self, request):
        serializer = BenefitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            benefit = serializer.save()
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='benefit_created',
                actor=request.user,
                target_type='benefit',
                target_id=benefit.pk,
            )
        return Response(BenefitSerializer(benefit).data, status=status.HTTP_201_CREATED)


class BenefitDetailView(APIView):
    """`PATCH /api/benefits/{id}/`."""

    permission_classes = [CanAccessBenefits]

    def patch(self, request, pk):
        benefit = get_object_or_404(Benefit, pk=pk)
        serializer = BenefitSerializer(benefit, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            benefit = serializer.save()
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='benefit_updated',
                actor=request.user,
                target_type='benefit',
                target_id=benefit.pk,
            )
        return Response(BenefitSerializer(benefit).data)


class BenefitEnrollmentListCreateView(APIView):
    """`GET, POST /api/employees/{id}/benefit-enrollments/`,
    `docs/06-api-contracts.md` §4.13."""

    permission_classes = [CanAccessBenefitEnrollments]

    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        enrollments = employee.benefit_enrollments.order_by('-enrolled_at')
        return Response(BenefitEnrollmentSerializer(enrollments, many=True).data)

    def post(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = BenefitEnrollmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            enrollment = serializer.save(employee=employee)
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='benefit_enrollment_created',
                actor=request.user,
                target_type='benefit_enrollment',
                target_id=enrollment.pk,
            )
        return Response(BenefitEnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)


class BenefitEnrollmentDetailView(APIView):
    """`PATCH /api/employees/{id}/benefit-enrollments/{enrollment_id}/`.
    `{"status": "cancelled"}` sets `cancelled_at`."""

    permission_classes = [CanAccessBenefitEnrollments]

    def patch(self, request, pk, enrollment_id):
        employee = get_object_or_404(Employee, pk=pk)
        enrollment = get_object_or_404(BenefitEnrollment, pk=enrollment_id, employee=employee)
        self.check_object_permissions(request, enrollment)
        serializer = BenefitEnrollmentUpdateSerializer(enrollment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            enrollment = serializer.save(cancelled_at=timezone.now())
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='benefit_enrollment_cancelled',
                actor=request.user,
                target_type='benefit_enrollment',
                target_id=enrollment.pk,
            )
        return Response(BenefitEnrollmentSerializer(enrollment).data)
