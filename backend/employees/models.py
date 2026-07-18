from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from departments.models import Department, JobTitle


class Employee(models.Model):
    """`employee`, `docs/05-database-schema.md` §4.4. SRS §6.1's central
    entity; HRMS-FR-001 to HRMS-FR-004, HRMS-FR-009, HRMS-FR-011,
    HRMS-FR-012; HRMS-BR-001 to HRMS-BR-003.
    """

    STATUS_ACTIVE = 'active'
    STATUS_ON_LEAVE = 'on_leave'
    STATUS_SUSPENDED = 'suspended'
    STATUS_TERMINATED = 'terminated'
    STATUS_RESIGNED = 'resigned'
    STATUS_RETIRED = 'retired'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_ON_LEAVE, 'On leave'),
        (STATUS_SUSPENDED, 'Suspended'),
        (STATUS_TERMINATED, 'Terminated'),
        (STATUS_RESIGNED, 'Resigned'),
        (STATUS_RETIRED, 'Retired'),
    ]

    employee_number = models.CharField(max_length=64, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    department = models.ForeignKey(Department, on_delete=models.RESTRICT, related_name='employees')
    job_title = models.ForeignKey(JobTitle, on_delete=models.RESTRICT, related_name='employees')
    employment_status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    hire_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employee'

    def __str__(self):
        return f'{self.employee_number} {self.first_name} {self.last_name}'


class EmploymentHistory(models.Model):
    """`employment_history`, `docs/05-database-schema.md` §4.4. HRMS-FR-004.
    One row per material change to an employee's job facts, written only by
    the status/department/job-title/manager-change endpoints, never directly.
    """

    EVENT_HIRED = 'hired'
    EVENT_STATUS_CHANGE = 'status_change'
    EVENT_DEPARTMENT_CHANGE = 'department_change'
    EVENT_JOB_TITLE_CHANGE = 'job_title_change'
    EVENT_MANAGER_CHANGE = 'manager_change'
    EVENT_CHOICES = [
        (EVENT_HIRED, 'Hired'),
        (EVENT_STATUS_CHANGE, 'Status change'),
        (EVENT_DEPARTMENT_CHANGE, 'Department change'),
        (EVENT_JOB_TITLE_CHANGE, 'Job title change'),
        (EVENT_MANAGER_CHANGE, 'Manager change'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT, related_name='employment_history')
    event_type = models.CharField(max_length=32, choices=EVENT_CHOICES)
    effective_date = models.DateField()
    previous_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField()
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'employment_history'
        verbose_name_plural = 'employment history'

    def __str__(self):
        return f'{self.event_type} for employee {self.employee_id}'


class EmployeeDocument(models.Model):
    """`employee_document`, `docs/05-database-schema.md` §4.4. HRMS-FR-006,
    HRMS-NFR-007, HRMS-NFR-008, HRMS-NFR-021. The file itself lives in
    S3-compatible object storage (ADR-0007); this table holds only metadata
    and the storage key.
    """

    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT, related_name='documents')
    document_type = models.CharField(max_length=64)
    object_key = models.CharField(max_length=512, unique=True)
    file_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=127)
    size_bytes = models.BigIntegerField(validators=[MinValueValidator(1)])
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'employee_document'

    def __str__(self):
        return f'{self.document_type} for employee {self.employee_id}'


class EmergencyContact(models.Model):
    """`emergency_contact`, `docs/05-database-schema.md` §4.4. HRMS-FR-007."""

    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT, related_name='emergency_contacts')
    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=100)
    phone = models.CharField(max_length=32)
    email = models.EmailField(null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'emergency_contact'

    def __str__(self):
        return f'{self.name} ({self.relationship}) for employee {self.employee_id}'
