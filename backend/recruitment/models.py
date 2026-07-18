from django.conf import settings
from django.db import models

from accounts.models import CASE_INSENSITIVE_COLLATION
from departments.models import Department, JobTitle
from employees.models import Employee


class JobRequisition(models.Model):
    """`job_requisition`, `docs/05-database-schema.md` §4.7. HRMS-FR-013, HRMS-FR-014."""

    STATUS_DRAFT = 'draft'
    STATUS_PENDING_APPROVAL = 'pending_approval'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PENDING_APPROVAL, 'Pending approval'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_CLOSED, 'Closed'),
    ]

    department = models.ForeignKey(Department, on_delete=models.RESTRICT, related_name='job_requisitions')
    job_title = models.ForeignKey(JobTitle, on_delete=models.RESTRICT, related_name='job_requisitions')
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name='requested_job_requisitions',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_requisition'

    def __str__(self):
        return f'requisition for {self.job_title} in {self.department} ({self.status})'


class JobPosting(models.Model):
    """`job_posting`, `docs/05-database-schema.md` §4.7. HRMS-FR-015, distinct from requisition per `CONTEXT.md`."""

    CHANNEL_INTERNAL = 'internal'
    CHANNEL_EXTERNAL = 'external'
    CHANNEL_CHOICES = [
        (CHANNEL_INTERNAL, 'Internal'),
        (CHANNEL_EXTERNAL, 'External'),
    ]

    requisition = models.ForeignKey(JobRequisition, on_delete=models.RESTRICT, related_name='postings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    channel = models.CharField(max_length=16, choices=CHANNEL_CHOICES)
    published_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_posting'

    def __str__(self):
        return self.title


class Candidate(models.Model):
    """`candidate`, `docs/05-database-schema.md` §4.7. HRMS-FR-016. `CONTEXT.md`:
    "a candidate is not an employee." No foreign key to `Employee` exists on
    this model; conversion creates a new, independent `Employee` row rather
    than mutating this one into it."""

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(db_collation=CASE_INSENSITIVE_COLLATION)
    phone = models.CharField(max_length=32, null=True, blank=True)
    resume_object_key = models.CharField(max_length=512, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'candidate'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class CandidateApplication(models.Model):
    """`candidate_application`, `docs/05-database-schema.md` §4.7. HRMS-FR-017.
    Separates the candidate's identity from a specific application, since a
    candidate is not confined to one posting."""

    STAGE_APPLIED = 'applied'
    STAGE_SCREENING = 'screening'
    STAGE_INTERVIEW = 'interview'
    STAGE_OFFER = 'offer'
    STAGE_HIRED = 'hired'
    STAGE_REJECTED = 'rejected'
    STAGE_CHOICES = [
        (STAGE_APPLIED, 'Applied'),
        (STAGE_SCREENING, 'Screening'),
        (STAGE_INTERVIEW, 'Interview'),
        (STAGE_OFFER, 'Offer'),
        (STAGE_HIRED, 'Hired'),
        (STAGE_REJECTED, 'Rejected'),
    ]

    candidate = models.ForeignKey(Candidate, on_delete=models.RESTRICT, related_name='applications')
    posting = models.ForeignKey(JobPosting, on_delete=models.RESTRICT, related_name='applications')
    stage = models.CharField(max_length=16, choices=STAGE_CHOICES, default=STAGE_APPLIED)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidate_application'

    def __str__(self):
        return f'{self.candidate} -> {self.posting} ({self.stage})'


class Interview(models.Model):
    """`interview`, `docs/05-database-schema.md` §4.7. HRMS-FR-018, HRMS-FR-019."""

    STATUS_SCHEDULED = 'scheduled'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    application = models.ForeignKey(CandidateApplication, on_delete=models.RESTRICT, related_name='interviews')
    interviewer_employee = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
    )
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    feedback = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'interview'

    def __str__(self):
        return f'interview for application {self.application_id} at {self.scheduled_at}'


class OfferLetter(models.Model):
    """`offer_letter`, `docs/05-database-schema.md` §4.7. HRMS-FR-020, HRMS-FR-021.

    `offered_pay_grade_id` is omitted from this module deliberately: it is a
    forward FK into `pay_grade`, owned by Module 15 (Compensation and
    Benefits), not yet built. Per this project's established
    provider-precedes-consumer handling (see issue RECRUIT-001), the column
    is added in a later migration once Module 15 lands.
    """

    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_WITHDRAWN = 'withdrawn'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_WITHDRAWN, 'Withdrawn'),
    ]

    application = models.ForeignKey(CandidateApplication, on_delete=models.RESTRICT, related_name='offers')
    offered_salary = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    issued_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    document_object_key = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        db_table = 'offer_letter'
        constraints = [
            models.CheckConstraint(check=models.Q(offered_salary__gte=0), name='offer_letter_offered_salary_non_negative'),
        ]

    def __str__(self):
        return f'offer for application {self.application_id} ({self.status})'
