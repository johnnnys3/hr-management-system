from django.conf import settings
from django.db import models

from employees.models import Employee
from recruitment.models import CandidateApplication


class OnboardingChecklist(models.Model):
    """`onboarding_checklist`, `docs/05-database-schema.md` §4.8. HRMS-FR-022,
    HRMS-FR-023, HRMS-BR-013. Created only at conversion — a checklist row's
    existence for a given employee is itself evidence that conversion
    happened correctly; a checklist row with no `employee` row is not a
    state this schema can represent.
    """

    employee = models.OneToOneField(Employee, on_delete=models.RESTRICT, related_name='onboarding_checklist')
    application = models.ForeignKey(
        CandidateApplication, on_delete=models.SET_NULL, null=True, blank=True, related_name='onboarding_checklists',
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'onboarding_checklist'

    def __str__(self):
        return f'onboarding for {self.employee}'


class OnboardingTask(models.Model):
    """`onboarding_task`, `docs/05-database-schema.md` §4.8. HRMS-FR-024."""

    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_SKIPPED = 'skipped'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_PROGRESS, 'In progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_SKIPPED, 'Skipped'),
    ]

    checklist = models.ForeignKey(OnboardingChecklist, on_delete=models.RESTRICT, related_name='tasks')
    name = models.CharField(max_length=255)
    is_required = models.BooleanField(default=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'onboarding_task'

    def __str__(self):
        return f'{self.name} ({self.status})'
