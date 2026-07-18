from django.db import models


class Department(models.Model):
    """`department`, `docs/05-database-schema.md` §4.5. HRMS-BR-002; SRS §2.7 HR configuration."""

    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'department'

    def __str__(self):
        return self.name


class JobTitle(models.Model):
    """`job_title`, `docs/05-database-schema.md` §4.5. HRMS-FR-003; grouped
    with Department under HR configuration rather than Employee Management,
    per `docs/07-iam-rbac.md` §4.2's HR configuration permission row.
    """

    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_title'

    def __str__(self):
        return self.name
