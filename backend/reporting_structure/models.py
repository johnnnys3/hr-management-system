from django.db import models

from employees.models import Employee


class ReportingRelationship(models.Model):
    """`reporting_relationship`, `docs/05-database-schema.md` §4.6.
    HRMS-FR-008, HRMS-BR-004. Current-state table: one row per employee who
    has a manager. An employee with none (top management, HRMS-BR-004's
    exception) has no row rather than a null-manager row.
    """

    employee = models.OneToOneField(Employee, on_delete=models.RESTRICT, related_name='reporting_relationship')
    manager_employee = models.ForeignKey(Employee, on_delete=models.RESTRICT, related_name='direct_reports')
    effective_from = models.DateField()

    class Meta:
        db_table = 'reporting_relationship'
        constraints = [
            models.CheckConstraint(
                check=~models.Q(employee=models.F('manager_employee')),
                name='reporting_relationship_not_self_managed',
            ),
        ]

    def __str__(self):
        return f'employee {self.employee_id} reports to {self.manager_employee_id}'
