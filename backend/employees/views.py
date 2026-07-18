from datetime import date

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

import audit.services
from audit.models import AuditLog
from iam.roles import HR_ADMINISTRATOR, HR_OFFICER, is_employee

from . import storage
from .models import EmergencyContact, Employee, EmployeeDocument, EmploymentHistory
from .permissions import (
    CanAccessEmergencyContacts,
    CanAccessEmployeeDocuments,
    CanAccessEmployeeRecords,
    IsOwnEmployeeRecord,
)
from .serializers import (
    EmergencyContactSerializer,
    EmployeeDocumentSerializer,
    EmployeeSelfServiceSerializer,
    EmployeeSerializer,
    EmployeeStatusUpdateSerializer,
    EmploymentHistorySerializer,
)

MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024  # HRMS-NFR-008's configurable upper bound

# `docs/06-api-contracts.md` §2.4's `?ordering=field`/`-field` over the
# fields this endpoint's table names as filterable — an allowlist, not a
# passthrough to `queryset.order_by()`, so an unrecognised field yields a
# clean `400` instead of an uncaught `FieldError`.
ALLOWED_ORDERING_FIELDS = {
    'employee_number', 'first_name', 'last_name', 'department_id', 'job_title_id',
    'employment_status', 'hire_date',
}


def _record_history(*, employee, event_type, previous_value, new_value, actor):
    return EmploymentHistory.objects.create(
        employee=employee,
        event_type=event_type,
        effective_date=date.today(),
        previous_value=previous_value,
        new_value=new_value,
        recorded_by=actor if getattr(actor, 'is_authenticated', False) else None,
    )


def _visible_employees(user):
    """`docs/07-iam-rbac.md` §5's Employee records row. Manager's "direct
    reports" cell is not implemented — `reporting_relationship` is Module 8;
    `is_manager` stays stubbed `False`, so a Manager with no other role
    resolves to the Employee branch below and, holding no `employee`
    record naming them, sees nothing either."""
    if user.groups.filter(name__in=[HR_OFFICER, HR_ADMINISTRATOR]).exists():
        return Employee.objects.all()
    if is_employee(user):
        return Employee.objects.filter(pk=user.employee_id)
    return Employee.objects.none()


class EmployeeListCreateView(APIView):
    """`GET, POST /api/employees/`, `docs/06-api-contracts.md` §4.3."""

    permission_classes = [CanAccessEmployeeRecords]

    def get(self, request):
        queryset = _visible_employees(request.user).order_by('employee_number')
        department_id = request.query_params.get('department_id')
        job_title_id = request.query_params.get('job_title_id')
        employment_status = request.query_params.get('employment_status')
        search = request.query_params.get('search')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        if job_title_id:
            queryset = queryset.filter(job_title_id=job_title_id)
        if employment_status:
            queryset = queryset.filter(employment_status=employment_status)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(employee_number__icontains=search)
            )
        ordering = request.query_params.get('ordering')
        if ordering:
            if ordering.lstrip('-') not in ALLOWED_ORDERING_FIELDS:
                return Response({'detail': 'unsupported ordering field.'}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.order_by(ordering)
        return Response(EmployeeSerializer(queryset, many=True).data)

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            employee = serializer.save(employment_status=Employee.STATUS_ACTIVE)
            _record_history(
                employee=employee,
                event_type=EmploymentHistory.EVENT_HIRED,
                previous_value=None,
                new_value={'employment_status': employee.employment_status, 'hire_date': str(employee.hire_date)},
                actor=request.user,
            )
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='employee_created',
                actor=request.user,
                target_type='employee',
                target_id=employee.pk,
            )
        return Response(EmployeeSerializer(employee).data, status=status.HTTP_201_CREATED)


class EmployeeDetailView(APIView):
    """`GET, PATCH /api/employees/{id}/`, `docs/06-api-contracts.md` §4.3.
    HR Officer's `PATCH` reaches the full record; HR Administrator's
    reaches `employment_status` only (`docs/07-iam-rbac.md` §4.2) — the
    view selects the narrower serializer for that role rather than
    trusting a shared one with a permission check bolted on.
    """

    permission_classes = [CanAccessEmployeeRecords]

    def _get_object(self, request, pk):
        employee = get_object_or_404(_visible_employees(request.user), pk=pk)
        return employee

    def get(self, request, pk):
        employee = self._get_object(request, pk)
        return Response(EmployeeSerializer(employee).data)

    def patch(self, request, pk):
        employee = self._get_object(request, pk)
        is_hr_administrator_only = (
            not request.user.groups.filter(name=HR_OFFICER).exists()
            and request.user.groups.filter(name=HR_ADMINISTRATOR).exists()
        )
        serializer_class = EmployeeStatusUpdateSerializer if is_hr_administrator_only else EmployeeSerializer

        previous = {
            'employment_status': employee.employment_status,
            'department_id': employee.department_id,
            'job_title_id': employee.job_title_id,
        }
        serializer = serializer_class(employee, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            employee = serializer.save()

            if 'employment_status' in request.data and previous['employment_status'] != employee.employment_status:
                _record_history(
                    employee=employee,
                    event_type=EmploymentHistory.EVENT_STATUS_CHANGE,
                    previous_value={'employment_status': previous['employment_status']},
                    new_value={'employment_status': employee.employment_status},
                    actor=request.user,
                )
            if 'department' in request.data and previous['department_id'] != employee.department_id:
                _record_history(
                    employee=employee,
                    event_type=EmploymentHistory.EVENT_DEPARTMENT_CHANGE,
                    previous_value={'department_id': previous['department_id']},
                    new_value={'department_id': employee.department_id},
                    actor=request.user,
                )
            if 'job_title' in request.data and previous['job_title_id'] != employee.job_title_id:
                _record_history(
                    employee=employee,
                    event_type=EmploymentHistory.EVENT_JOB_TITLE_CHANGE,
                    previous_value={'job_title_id': previous['job_title_id']},
                    new_value={'job_title_id': employee.job_title_id},
                    actor=request.user,
                )

            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='employee_updated',
                actor=request.user,
                target_type='employee',
                target_id=employee.pk,
            )
        return Response(EmployeeSerializer(employee).data)


class EmployeeMeView(APIView):
    """`GET, PATCH /api/employees/me/`, `docs/06-api-contracts.md` §4.3."""

    permission_classes = [IsOwnEmployeeRecord]

    def get(self, request):
        return Response(EmployeeSelfServiceSerializer(request.user.employee).data)

    def patch(self, request):
        employee = request.user.employee
        serializer = EmployeeSelfServiceSerializer(employee, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            employee = serializer.save()
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='employee_self_service_updated',
                actor=request.user,
                target_type='employee',
                target_id=employee.pk,
            )
        return Response(EmployeeSelfServiceSerializer(employee).data)


class EmploymentHistoryListView(APIView):
    """`GET /api/employees/{id}/employment-history/`, read-only over
    `employment_history` — written only by the change endpoints above."""

    permission_classes = [CanAccessEmployeeRecords]

    def get(self, request, pk):
        employee = get_object_or_404(_visible_employees(request.user), pk=pk)
        history = employee.employment_history.order_by('-effective_date', '-created_at')
        return Response(EmploymentHistorySerializer(history, many=True).data)


class EmployeeDocumentListCreateView(APIView):
    """`GET, POST /api/employees/{id}/documents/`, `docs/06-api-contracts.md`
    §4.3. `POST` is multipart; `object_key` is generated and content type
    is validated server-side by inspection (ADR-0007)."""

    permission_classes = [CanAccessEmployeeDocuments]
    parser_classes = [MultiPartParser, FormParser]

    def _get_employee(self, request, pk):
        return get_object_or_404(_visible_employees(request.user), pk=pk)

    def get(self, request, pk):
        employee = self._get_employee(request, pk)
        documents = employee.documents.order_by('-created_at')
        return Response(EmployeeDocumentSerializer(documents, many=True).data)

    def post(self, request, pk):
        employee = self._get_employee(request, pk)
        uploaded_file = request.data.get('file')
        document_type = request.data.get('document_type')
        if not uploaded_file or not document_type:
            return Response({'detail': 'file and document_type are required.'}, status=status.HTTP_400_BAD_REQUEST)
        if uploaded_file.size > MAX_DOCUMENT_SIZE_BYTES:
            return Response({'detail': 'file exceeds the maximum allowed size.'}, status=status.HTTP_400_BAD_REQUEST)

        content_type = storage.sniff_content_type(uploaded_file)
        if content_type is None:
            return Response({'detail': 'unrecognised file type.'}, status=status.HTTP_400_BAD_REQUEST)

        object_key = storage.generate_object_key(employee.pk, content_type)
        storage.save_document(object_key, uploaded_file)

        try:
            with transaction.atomic():
                document = EmployeeDocument.objects.create(
                    employee=employee,
                    document_type=document_type,
                    object_key=object_key,
                    file_name=uploaded_file.name,
                    content_type=content_type,
                    size_bytes=uploaded_file.size,
                    uploaded_by=request.user,
                )
                audit.services.record(
                    category=AuditLog.CATEGORY_RECORD_CHANGE,
                    action='employee_document_uploaded',
                    actor=request.user,
                    target_type='employee_document',
                    target_id=document.pk,
                )
        except Exception:
            # The object was already written to storage before this block;
            # a failed metadata write must not leave it orphaned there with
            # no `employee_document` row pointing to it.
            storage.delete_document(object_key)
            raise
        return Response(EmployeeDocumentSerializer(document).data, status=status.HTTP_201_CREATED)


class EmployeeDocumentDownloadView(APIView):
    """`GET /api/employees/{id}/documents/{doc_id}/download/`. Returns a
    short-lived signed URL, never the file bytes (ADR-0007 — the bucket is
    private)."""

    permission_classes = [CanAccessEmployeeDocuments]

    def get(self, request, pk, doc_id):
        employee = get_object_or_404(_visible_employees(request.user), pk=pk)
        document = get_object_or_404(EmployeeDocument, pk=doc_id, employee=employee)
        return Response({'url': storage.signed_download_url(document.object_key)})


class EmergencyContactListCreateView(APIView):
    """`GET, POST /api/employees/{id}/emergency-contacts/`,
    `docs/06-api-contracts.md` §4.3."""

    permission_classes = [CanAccessEmergencyContacts]

    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        contacts = employee.emergency_contacts.order_by('-is_primary', 'name')
        return Response(EmergencyContactSerializer(contacts, many=True).data)

    def post(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmergencyContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            contact = serializer.save(employee=employee)
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='emergency_contact_created',
                actor=request.user,
                target_type='emergency_contact',
                target_id=contact.pk,
            )
        return Response(EmergencyContactSerializer(contact).data, status=status.HTTP_201_CREATED)


class EmergencyContactDetailView(APIView):
    """`PATCH /api/employees/{id}/emergency-contacts/{contact_id}/`. Split
    from the collection endpoint the same way `departments`' list/detail
    views are, so `PATCH` targets one contact rather than the collection
    `docs/06-api-contracts.md` §4.3 groups it under."""

    permission_classes = [CanAccessEmergencyContacts]

    def patch(self, request, pk, contact_id):
        employee = get_object_or_404(Employee, pk=pk)
        contact = get_object_or_404(EmergencyContact, pk=contact_id, employee=employee)
        serializer = EmergencyContactSerializer(contact, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            contact = serializer.save()
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='emergency_contact_updated',
                actor=request.user,
                target_type='emergency_contact',
                target_id=contact.pk,
            )
        return Response(EmergencyContactSerializer(contact).data)
