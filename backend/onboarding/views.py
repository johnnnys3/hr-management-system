from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import audit.services
from audit.models import AuditLog
from departments.models import Department, JobTitle
from employees.models import Employee
from recruitment.models import CandidateApplication, OfferLetter

from .models import OnboardingChecklist, OnboardingTask
from .permissions import CanAccessOnboarding, CanConvert
from .serializers import (
    ConvertDirectHireSerializer,
    ConvertFromApplicationSerializer,
    OnboardingChecklistSerializer,
    OnboardingTaskSerializer,
    OnboardingTaskStatusUpdateSerializer,
)


class ConvertView(APIView):
    """`POST /api/onboarding/convert/`, `docs/06-api-contracts.md` §4.7. The
    HRMS-BR-013 conversion point: creates the `employee` row, then the
    `onboarding_checklist` row referencing it, and — when converting from an
    `application_id` — transitions the source `candidate_application.stage`
    to `hired` in the same transaction. Atomic: a failure partway does not
    leave an `employee` row with no checklist, nor an application stuck
    reading `offer` after conversion has already happened.
    """

    permission_classes = [CanConvert]

    def post(self, request):
        if 'application_id' in request.data:
            return self._convert_from_application(request)
        return self._convert_direct_hire(request)

    def _convert_from_application(self, request):
        serializer = ConvertFromApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        get_object_or_404(Department, pk=data['department'])
        get_object_or_404(JobTitle, pk=data['job_title'])
        with transaction.atomic():
            application = get_object_or_404(
                CandidateApplication.objects.select_for_update(), pk=data['application_id'].pk,
            )
            if application.stage != CandidateApplication.STAGE_OFFER:
                return Response(
                    {'detail': f'application is not at the offer stage (stage {application.stage!r}).'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            has_accepted_offer = OfferLetter.objects.filter(
                application=application, status=OfferLetter.STATUS_ACCEPTED,
            ).exists()
            if not has_accepted_offer:
                return Response(
                    {'detail': 'application has no accepted offer.'}, status=status.HTTP_400_BAD_REQUEST,
                )
            candidate = application.candidate
            employee = Employee.objects.create(
                employee_number=data['employee_number'],
                first_name=candidate.first_name,
                last_name=candidate.last_name,
                date_of_birth=data['date_of_birth'],
                department_id=data['department'],
                job_title_id=data['job_title'],
                hire_date=data['hire_date'],
            )
            checklist = OnboardingChecklist.objects.create(employee=employee, application=application)
            application.stage = CandidateApplication.STAGE_HIRED
            application.save(update_fields=['stage', 'updated_at'])
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='onboarding_converted',
                actor=request.user,
                target_type='onboarding_checklist',
                target_id=checklist.pk,
            )
        return Response(OnboardingChecklistSerializer(checklist).data, status=status.HTTP_201_CREATED)

    def _convert_direct_hire(self, request):
        serializer = ConvertDirectHireSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        get_object_or_404(Department, pk=data['department'])
        get_object_or_404(JobTitle, pk=data['job_title'])
        with transaction.atomic():
            employee = Employee.objects.create(
                employee_number=data['employee_number'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                date_of_birth=data['date_of_birth'],
                department_id=data['department'],
                job_title_id=data['job_title'],
                hire_date=data['hire_date'],
            )
            checklist = OnboardingChecklist.objects.create(employee=employee, application=None)
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='onboarding_converted',
                actor=request.user,
                target_type='onboarding_checklist',
                target_id=checklist.pk,
            )
        return Response(OnboardingChecklistSerializer(checklist).data, status=status.HTTP_201_CREATED)


class OnboardingChecklistDetailView(APIView):
    """`GET /api/onboarding-checklists/{id}/`, `docs/06-api-contracts.md` §4.7."""

    permission_classes = [CanAccessOnboarding]

    def get(self, request, pk):
        checklist = get_object_or_404(OnboardingChecklist, pk=pk)
        return Response(OnboardingChecklistSerializer(checklist).data)


class OnboardingTaskListCreateView(APIView):
    """`GET, POST /api/onboarding-checklists/{id}/tasks/`, `docs/06-api-contracts.md` §4.7."""

    permission_classes = [CanAccessOnboarding]

    def get(self, request, pk):
        checklist = get_object_or_404(OnboardingChecklist, pk=pk)
        tasks = checklist.tasks.order_by('id')
        return Response(OnboardingTaskSerializer(tasks, many=True).data)

    def post(self, request, pk):
        checklist = get_object_or_404(OnboardingChecklist, pk=pk)
        serializer = OnboardingTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            task = serializer.save(checklist=checklist)
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='onboarding_task_created',
                actor=request.user,
                target_type='onboarding_task',
                target_id=task.pk,
            )
        return Response(OnboardingTaskSerializer(task).data, status=status.HTTP_201_CREATED)


class OnboardingTaskDetailView(APIView):
    """`PATCH /api/onboarding-checklists/{id}/tasks/{task_id}/`, `docs/06-api-contracts.md` §4.7.
    `PATCH {"status": "completed"}` sets `completed_by`, `completed_at`.
    """

    permission_classes = [CanAccessOnboarding]

    def patch(self, request, pk, task_id):
        task = get_object_or_404(OnboardingTask, pk=task_id, checklist_id=pk)
        serializer = OnboardingTaskStatusUpdateSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            new_status = serializer.validated_data.get('status', task.status)
            was_completed = task.status == OnboardingTask.STATUS_COMPLETED
            task.status = new_status
            if new_status == OnboardingTask.STATUS_COMPLETED and not was_completed:
                task.completed_by = request.user
                task.completed_at = timezone.now()
            elif new_status != OnboardingTask.STATUS_COMPLETED:
                task.completed_by = None
                task.completed_at = None
            task.save(update_fields=['status', 'completed_by', 'completed_at'])
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='onboarding_task_updated',
                actor=request.user,
                target_type='onboarding_task',
                target_id=task.pk,
            )
        return Response(OnboardingTaskSerializer(task).data)
