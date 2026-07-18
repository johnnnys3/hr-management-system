from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import audit.services
from audit.models import AuditLog

from .models import Department, JobTitle
from .permissions import CanAccessHRConfiguration
from .serializers import DepartmentSerializer, JobTitleSerializer


class DepartmentListCreateView(APIView):
    """`GET, POST /api/departments/`, `docs/06-api-contracts.md` §4.4."""

    permission_classes = [CanAccessHRConfiguration]

    def get(self, request):
        """
        List all departments ordered by name.
        
        Returns:
            Response: A serialized list of departments.
        """
        serializer = DepartmentSerializer(Department.objects.order_by('name'), many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a department from the submitted data and record its creation.
        
        Parameters:
        	request: The request containing the department data and authenticated user.
        
        Returns:
        	Response: The created department data with HTTP 201 Created status.
        """
        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        department = serializer.save()
        audit.services.record(
            category=AuditLog.CATEGORY_RECORD_CHANGE,
            action='department_created',
            actor=request.user,
            target_type='department',
            target_id=department.pk,
        )
        return Response(DepartmentSerializer(department).data, status=status.HTTP_201_CREATED)


class DepartmentDetailView(APIView):
    """`PATCH /api/departments/{id}/`, `docs/06-api-contracts.md` §4.4.
    `PATCH {"is_active": false}` retires rather than deletes, per
    `docs/05-database-schema.md` §2.3 — there is no `DELETE`.
    """

    permission_classes = [CanAccessHRConfiguration]

    def patch(self, request, pk):
        """
        Partially updates a department and records the change for auditing.
        
        Parameters:
            pk: The primary key of the department to update.
        
        Returns:
            The updated department data.
        """
        department = get_object_or_404(Department, pk=pk)
        serializer = DepartmentSerializer(department, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        audit.services.record(
            category=AuditLog.CATEGORY_RECORD_CHANGE,
            action='department_updated',
            actor=request.user,
            target_type='department',
            target_id=department.pk,
        )
        return Response(DepartmentSerializer(department).data)


class JobTitleListCreateView(APIView):
    """`GET, POST /api/job-titles/`, `docs/06-api-contracts.md` §4.4."""

    permission_classes = [CanAccessHRConfiguration]

    def get(self, request):
        """
        Retrieve all job titles ordered alphabetically by name.
        
        Returns:
            Response: A serialized list of job titles.
        """
        serializer = JobTitleSerializer(JobTitle.objects.order_by('name'), many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a job title from the submitted data and record the creation event.
        
        Parameters:
        	request: The request containing the job title data.
        
        Returns:
        	Response: The created job title with an HTTP 201 Created status.
        """
        serializer = JobTitleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job_title = serializer.save()
        audit.services.record(
            category=AuditLog.CATEGORY_RECORD_CHANGE,
            action='job_title_created',
            actor=request.user,
            target_type='job_title',
            target_id=job_title.pk,
        )
        return Response(JobTitleSerializer(job_title).data, status=status.HTTP_201_CREATED)


class JobTitleDetailView(APIView):
    """`PATCH /api/job-titles/{id}/`, `docs/06-api-contracts.md` §4.4."""

    permission_classes = [CanAccessHRConfiguration]

    def patch(self, request, pk):
        """
        Partially updates an existing job title and records the change.
        
        Parameters:
            pk (int): Primary key of the job title to update.
        
        Returns:
            Response: The updated job title data.
        
        Raises:
            Http404: If the job title does not exist.
        """
        job_title = get_object_or_404(JobTitle, pk=pk)
        serializer = JobTitleSerializer(job_title, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        audit.services.record(
            category=AuditLog.CATEGORY_RECORD_CHANGE,
            action='job_title_updated',
            actor=request.user,
            target_type='job_title',
            target_id=job_title.pk,
        )
        return Response(JobTitleSerializer(job_title).data)
